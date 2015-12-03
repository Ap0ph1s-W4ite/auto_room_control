// This is simple access to the I2c bus, how it should be: low level
// no restrictions simple to use.
//
// * Copyright (C) 2013 Jim Spence <jim@byvac.com>
// * www.byvac.com
//
// * This program is free software; you can redistribute it and/or modify
// * it under the terms of the GNU General Public License as published by
// * the Free Software Foundation; version 2 of the License.
//
// Thanks to Mark M. Hoffman <mhoffman@lightlink.com, for smbus of which in
// particular I copied the 'type' items
// also: http://www.mjmwired.net/kernel/Documentation/i2c/dev-interface
//
// Very simple to use:
// from notsmb import notSMB
// bus = notSMB(0) // assuming i2cbus 0
// result = i2c(<address>,[list to send],number of items to receive)
// list to send can be 0 and items to receive can be 0, reult is a list
//
// Version 1.0 September 2013
// Version 1.1 October 2013
//      Added delay to write and read - could do with some kind of ready signal
// Version 1.2 April 2014
//      Increased write delay, WDELAY now controls this

#include <Python.h>
#include <fcntl.h>
#include <errno.h>
#include <stdio.h>
#include <sys/time.h>
#include <unistd.h>
#include <linux/ioctl.h>

//#include <linux/i2c.h>
#include <linux/i2c-dev.h>

//
#define WDELAY 5000

PyDoc_STRVAR(notSMB_doc,
	"Alternative to SMBus, why so complex when 1 function will do!!\n"
	"\n");

typedef struct {
	PyObject_HEAD

	int fd;		/* open file descriptor: /dev/i2c-?, or -1 */
	int addr;	/* current client SMBus address */
} notSMB;

static PyObject *notSMB_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
	notSMB *self;

	if ((self = (notSMB *)type->tp_alloc(type, 0)) == NULL)
		return NULL;

	self->fd = -1;
	self->addr = -1;

	return (PyObject *)self;
}


#define MAXPATH 16
// *****************************************************************************
PyDoc_STRVAR(notSMB_open_doc,
	"\nopen - not sure if this is ever needed"
	"");
// *****************************************************************************
static PyObject* notsmb_open(notSMB *self, PyObject *args)
{
	int bus;
	char path[MAXPATH];

	if (!PyArg_ParseTuple(args, "i", &bus))
		return NULL;

	if (snprintf(path, MAXPATH, "/dev/i2c-%d", bus) >= MAXPATH) {
		PyErr_SetString(PyExc_OverflowError,
			"Bus number is invalid.");
		return NULL;
	}

	if ((self->fd = open(path, O_RDWR, 0)) == -1) {
		PyErr_SetFromErrno(PyExc_IOError);
		return NULL;
	}

	Py_INCREF(Py_None);
	return Py_None;
}

// *****************************************************************************
PyDoc_STRVAR(notSMB_close_doc,
	"\nclose"
	"");
// *****************************************************************************
static PyObject* notsmb_close(notSMB *self)
{
	if ((self->fd != -1) && (close(self->fd) == -1)) {
		PyErr_SetFromErrno(PyExc_IOError);
		return NULL;
	}

    close(self->fd);

	self->fd = -1;
	self->addr = -1;

	Py_INCREF(Py_None);
	return Py_None;

}


// *****************************************************************************
// gets a list from user an places it into a char array, the bfirt byte
// is the size - similar to SMBus
// *****************************************************************************
static int notsmb_list_to_data(PyObject *list, char *data)
{
	static char *msg = "Third argument must be a list of at least one, "
				"but not more than 32 integers";
	int ii, len,count=0;

	if (!PyList_Check(list)) {
		PyErr_SetString(PyExc_TypeError, msg);
		return 0; /* fail */
	}

	if ((len = PyList_GET_SIZE(list)) > 32) {
		PyErr_SetString(PyExc_OverflowError, msg);
		return 0; /* fail */
	}

	/* first byte is the length */
	*(data+count++) = (__u8)len;

	for (ii = 0; ii < len; ii++) {
		PyObject *val = PyList_GET_ITEM(list, ii);
		if (!PyInt_Check(val)) {
			PyErr_SetString(PyExc_TypeError, msg);
			return 0; /* fail */
		}
		*(data+ii+1) = (__u8)PyInt_AS_LONG(val);
	}

	return 1; /* success */
}

// *****************************************************************************
PyDoc_STRVAR(notSMB_i2c_doc,
	"\ni2c"
    "\nresult = i2c(<address>,[list to send],number of items to receive)"
    "\nlist to send can be 0 and items to receive can be 0, reult is a list"
	"\nuse in the format bus.i2c(adr,[wlist],n)"
	"");
// *****************************************************************************
static PyObject* notsmb_i2c(notSMB* self, PyObject* args)
{
    const char* adr;
    char write_data[32], wbuf[32], rbuf[32], rbytes;
    char wlen;
    int j;

    if (!PyArg_ParseTuple(args, "iO&i", &adr,
            notsmb_list_to_data, &write_data, &rbytes))
        return NULL;

    // Set address
    if (ioctl(self->fd, I2C_SLAVE, adr) < 0) {
        PyErr_SetString(PyExc_TypeError, "Error set address fail");
        return NULL;
    }

    // WRITE (if any)
    // write data is in write_data[], the first byte contains the
    // length of the data obtained from the list
    wlen= write_data[0];

    if(wlen) {  // shift buffer
        for(j=0;j<wlen;j++) {
            wbuf[j] = write_data[j+1];
        }
    }

    if(write(self->fd, wbuf, wlen) != wlen){
        PyErr_SetString(PyExc_TypeError, "Error write fail");
        return NULL;
    }
    // delay based on length of write
    usleep(WDELAY*wlen);

    // READ (if any)
    PyObject *list = PyList_New(rbytes);

    if(rbytes) {
        if (read(self->fd, rbuf, rbytes) != rbytes) {
            PyErr_SetString(PyExc_TypeError, "Error read fail");
            return NULL;
        }

        for(j=0;j<rbytes;j++) {
            PyObject *val = Py_BuildValue("l", (long)rbuf[j]);
            PyList_SET_ITEM(list, j, val);
        }
    }
    // delay based on length of read
    usleep(WDELAY*rbytes);


    return list;
}

// *****************************************************************************
PyDoc_STRVAR(notSMB_discover_doc,
	"\nsetect()"
	"\nreturns a list of i2c devices on the bus");
// *****************************************************************************
static PyObject* notsmb_discover(notSMB* self)
{
    int t;
    char j,rbytes=0xe0, wbuf[5];

    PyObject *list = PyList_New(0);

    for(j=0x10;j<rbytes;j++) {
        // Set address
        t = ioctl(self->fd, I2C_SLAVE, j); // there will be errors
        if(write(self->fd, wbuf, 0) == 0) {
            PyObject *val = Py_BuildValue("l", (long)j);
            PyList_Append(list, val);
        }
    }

   if(PyList_Size(list)>0) return list;
   else return Py_None;
}

// -----------------------------------------------------------------------------

static int notSMB_init(notSMB *self, PyObject *args, PyObject *kwds)
{
	int bus = -1;

	static char *kwlist[] = {"bus", NULL};

	if (!PyArg_ParseTupleAndKeywords(args, kwds, "|i:__init__",
			kwlist, &bus))
		return -1;

	if (bus >= 0) {
		notsmb_open(self, args);
		if (PyErr_Occurred())
			return -1;
	}

	return 0;
}

static void notSMB_dealloc(notSMB *self)
{
	PyObject *ref = notsmb_close(self);
	Py_XDECREF(ref);

	self->ob_type->tp_free((PyObject *)self);
}


PyDoc_STRVAR(notSMB_type_doc,
	"SMBus([bus]) -> SMBus\n\n"
	"Return a new SMBus object that is (optionally) connected to the\n"
	"specified I2C device interface.\n");

static PyMethodDef notSMBmethods[] =
{
	 {"open", (PyCFunction)notsmb_open, METH_VARARGS, notSMB_open_doc},
	 {"close", (PyCFunction)notsmb_close,  METH_NOARGS, notSMB_close_doc},
     {"i2c", (PyCFunction)notsmb_i2c, METH_VARARGS, notSMB_i2c_doc},
     {"detect", (PyCFunction)notsmb_discover, METH_NOARGS, notSMB_discover_doc},
     {NULL, NULL, 0, NULL}
};

static PyTypeObject notSMB_type = {
	PyObject_HEAD_INIT(NULL)
	0,				/* ob_size */
	"notSMB",			/* tp_name */
	sizeof(notSMB),			/* tp_basicsize */
	0,				/* tp_itemsize */
	(destructor)notSMB_dealloc,	/* tp_dealloc */
	0,				/* tp_print */
	0,				/* tp_getattr */
	0,				/* tp_setattr */
	0,				/* tp_compare */
	0,				/* tp_repr */
	0,				/* tp_as_number */
	0,				/* tp_as_sequence */
	0,				/* tp_as_mapping */
	0,				/* tp_hash */
	0,				/* tp_call */
	0,				/* tp_str */
	0,				/* tp_getattro */
	0,				/* tp_setattro */
	0,				/* tp_as_buffer */
	Py_TPFLAGS_DEFAULT,		/* tp_flags */
	notSMB_type_doc,			/* tp_doc */
	0,				/* tp_traverse */
	0,				/* tp_clear */
	0,				/* tp_richcompare */
	0,				/* tp_weaklistoffset */
	0,				/* tp_iter */
	0,				/* tp_iternext */
	notSMBmethods,			/* tp_methods */
	0,				/* tp_members */
	0,			/* tp_getset */
	0,				/* tp_base */
	0,				/* tp_dict */
	0,				/* tp_descr_get */
	0,				/* tp_descr_set */
	0,				/* tp_dictoffset */
	(initproc)notSMB_init,		/* tp_init */
	0,				/* tp_alloc */
	notSMB_new,			/* tp_new */
};

static PyMethodDef notSMB_module_methods[] = {
	{NULL}
};

PyMODINIT_FUNC
initnotsmb(void)
{
	PyObject* m;

	if (PyType_Ready(&notSMB_type) < 0)
		return;

	m = Py_InitModule3("notsmb", notSMB_module_methods, notSMB_doc);

	Py_INCREF(&notSMB_type);
	PyModule_AddObject(m, "notSMB", (PyObject *)&notSMB_type);
}

//PyMODINIT_FUNC
//initnotsmb(void)
//{
//     (void) Py_InitModule("notsmb", notSMBmethods);
//}

