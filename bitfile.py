"""Read and write files an arbitrary number of bits at a time.
************************************************************************

    File    : bitfile.py
    Purpose : This file implements a simple class of I/O methods for
              files that contain data in sizes that aren't integral
              bytes.  The methods contained in this class were created
              with compression algorithms in mind, but may be suited to
              other applications.
    Author  : Michael Dipperstein
    Date    : January 14, 2010

************************************************************************

bitfile: A python I/O class for files containing arbitrary data sizes.
Copyright (C) 2010
      Michael Dipperstein (mdipper@alumni.engr.ucsb.edu)

This file implements bitfile.

Bitfile is free software; you can redistribute it and/or modify it under
the terms of the GNU General Public License as published by the
Free Software Foundation; either version 3 of the License, or (at your
option) any later version.

Bitfile is distributed in the hope that it will be useful, but WITHOUT
ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public
License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import errno


def str_to_int(str):
    """Convert a str type variable to an int using ord of characters.

    This is a helper function that accepts a python string and converts
    it to an integer where ord(str[0]) is the MSB of the integer and
    ord(str[-1]) is the LSB of the integer.

    Arguments:
        str - The python string to be converted to an integer.

    Return Value(s):
        An integer where ord(str[0]) is the MSB of the integer and
        ord(str[-1]) is the LSB of the integer.

    Side Effects:
        None.

    Exceptions Raised:
        None.

    """

    bin_val = 0
    for i in xrange(len(str)):
        bin_val = (bin_val << 8) + ord(str[i])
    return bin_val


def int_to_str(value, length):
    """Convert an int type variable to a str using chr of bytes.

    This is a helper function that accepts a python integer and converts
    it to a string where chr(MSB) is str[0] and chr(LSB) is str[-1]

    Arguments:
        value - The python integer to be converted to a string.
        length - The number of bytes in the integer to be converted.

    Return Value(s):
        A string representation of an integer where ord(str[0]) is the
        MSB of the integer and ord(str[-1]) is the LSB of the integer.

    Side Effects:
        None.

    Exceptions Raised:
        None.

    """

    val_str = ''
    for i in xrange(length):
        val_str = chr(value & 0xFF) + val_str
        value = value >> 8
    return val_str


class BitFile:

    """Methods used to read and write files an N bits at a time.

    Methods:
        _verify_opened - Raise a ValueError if the file is not open.
        open - Opens an input or output bit file stream.
        close - Closes an opened input or output bit file stream.
        byte_align - Writes out buffered bits + enough spare bits to
                     align the data stream to the next full byte.
        flush - Flushes the output stream.
        get_char - Reads a character from the input stream.
        put_char - Writes a character to the output stream.
        get_bit - Reads a bit from the input stream.
        put_bit - Writes a bit to the output stream.
        get_bits_mtol - Reads multiple bits from the input stream
            (MSB to LSB).
        put_bits_mtol - Writes multiple bits to the output stream
            (MSB to LSB).
        get_bits_ltom - Reads multiple bits from the input stream
            (LSB to MSB).
        put_bits_ltom - Writes multiple bits to the output stream
            (LSB to MSB).

    Instance Variables:
        _stream - A pointer to the file stream.
        _mode - The mode of the file stream (read, write, append, ...)
        _input_buffer - A buffer for storing unread from bytes.
        _output_buffer - A buffer for aggregating bits written into bytes.

    """

    def __init__(self):
        """Constructor for BitFile class.

        This is the constructor function of the BitFile class. It
        creates a BitFile object and initializes all of it's data.

        Arguments:
            None.

        Return Value(s):
            An initialized BitFile object.

        Side Effects:
            Data elements are initialized as follows:
            _stream = None
            _mode = ''
            _input_buffer = [0, 0]
            _output_buffer = [0, 0]

        Exceptions Raised:
            None.

        """

        self._stream = None
        self._mode = ''

        # buffers are in the format [bit_count, buffered_bits]
        self._input_buffer = [0, 0]
        self._output_buffer = [0, 0]
        return

    def __del__(self):
        """Destructor for BitFile class.

        This is the Destructor function of the BitFile class. It flushes
        and closes an open BitFile file stream prior to object deletion.

        Arguments:
            None.

        Return Value(s):
            None.

        Side Effects:
            If the object's file stream is opened, it will be flushed
            and closed.

        Exceptions Raised:
            None.

        """

        if self._stream is not None and not self._stream.closed:
            self._stream.close()

    def _verify_opened(self):
        """Raise an exception if the file stream is not opened.

        This method will raise a ValueError exception if the object's
        file stream is not open.

        Arguments:
            None.

        Return Value(s):
            None.

        Side Effects:
            None.

        Exceptions Raised:
            ValueError - Raised when an object's file stream is no open.

        """

        if self._stream is None or self._stream.closed:
            raise ValueError('I/O operation on closed file.')
        return

    def _is_readable(self):
        """Returns True if there if the current steam can be read.

        This method will return True if there is a stream that is opened
        and readable (mode = 'rb' or 'r+b').

        Arguments:
            None.

        Return Value(s):
            None.

        Side Effects:
            None.

        Exceptions Raised:
            None.

        """

        if self._stream is not None and 'r' in self._mode:
            return True
        else:
            return False

    def _is_writable(self):
        """Returns True if there if the current steam can be read.

        This method will return True if there is a stream that is opened
        and writable (mode = 'wb' or 'ab' or 'r+b').

        Arguments:
            None.

        Return Value(s):
            None.

        Side Effects:
            None.

        Exceptions Raised:
            None.

        """

        if self._stream is not None and\
            any(['w' in self._mode, 'a' in self._mode, '+' in self._mode]):
            return True
        else:
            return False

    def open(self, file_name, mode):
        """Open a BitFile stream.

        This method will open the specified file as a BitFile stream.
        The file may no be opened as a text file.  A ValueError will be
        raised if text mode is requested.  Otherwise the file will be
        explicitly opened in binary mode.

        Arguments:
            file_name - The name of the file to be opened.
            mode - The mode the file is opened as ('rb', 'wb', 'ab')

        Return Value(s):
            None.

        Side Effects:
            _bit_buffer and _bit_count will be set to zero.

        Exceptions Raised:
            ValueError - Raised when a text mode is requested.
            ValueError - Raised when both read and write mode are requested.

        """

        if self._stream is None or self._stream.closed:
            if 't' in mode or 'U' in mode:
                raise ValueError('text mode not supported.')

            if 'b' not in mode:
                # Force binary mode in case this we're using ms windows.
                mode = mode + 'b'

            # open function will throw exception for other invalid modes.
            self._stream = open(file_name, mode)
            self._mode = mode
            self._input_buffer = [0, 0]
            self._output_buffer = [0, 0]
        else:
            raise ValueError('I/O operation on opened file.')
        return

    def close(self):
        """Close a BitFile stream.

        This method will close the specified file as a BitFile stream.
        It's associated bit buffer will be flushed with any spare bits
        being set to 0.  A ValueError will be raised if the stream is
        already closed.

        Arguments:
            None.

        Return Value(s):
            None.

        Side Effects:
            _stream will be set to None.
            _mode will be cleared.
            _output_buffer will be zeroed.

        Exceptions Raised:
            ValueError - Raised if the stream is already closed.

        """

        self._verify_opened()

        if self._is_writable() and self._output_buffer[0] != 0:
            # Writable file with buffered bits.  Flush output_buffer.
            self.flush(False)

        self._stream.close()
        self._stream = None
        self._mode = ''
        self._input_buffer = [0, 0]
        self._output_buffer = [0, 0]
        return

    def byte_align(self):
        """Aligns data stream to a byte boundary.

        This method aligns a BitFile stream to a byte boundary.  Output
        streams will be flushed with any spare bits being set to 0.
        Input streams will discard their buffered bits.  A ValueError
        will be raised if the stream is not open.

        Arguments:
            None.

        Return Value(s):
            None.

        Side Effects:
            Any buffered bits will be written to an output stream.
            All buffers will be zeroed.

        Exceptions Raised:
            ValueError - Raised if the stream is not opened.

        """

        self._verify_opened()

        return_value = self._output_buffer[1]

        if self._is_writable() and self._output_buffer[0] != 0:
            # Write out any unwritten bits.
            bits = self._output_buffer[1] << (8 - self._output_buffer[0])
            self._stream.write(chr(bits))

        self._input_buffer = [0, 0]
        self._output_buffer = [0, 0]
        return return_value

    def seek(self, offset, whence=0):
        """Seeks to the specified position in a BitFile stream.

        This method exposes Python's seek method for file objects.
        Since seek offsets are specified in terms of bytes, the BitFile
        stream will be byte aligned prior to the seek.

        Arguments:
            offset - The number of bytes to seek from whence position.
            whence - The position that offset is referenced from.
                     os.SEEK_SET (0) - absolute file positioning.
                     os.SEEK_CUR (1) - relative to the current position.
                     os.SEEK_END (2) - relative to the end of file.

        Return Value(s):
            None.

        Side Effects:
            Any buffered bits will be written to an output stream.
            _output_buffer will be zeroed.
            The current file position will be set to the seek location.

        Exceptions Raised:
            ValueError - Raised if the stream is not opened.
            Other exceptions may be raised by the seek function.

        """
        self.byte_align()
        self._stream.seek(offset, whence)

    def flush(self, ones_fill=False):
        """Flushes the bit buffer of an output stream.

        This method flushes a BitFile's bit buffer, writing it to the
        output streams.  Any spare bits being set to 0 unless ones_fill
        is True.  A ValueError will be raised if the stream is not open.
        IOError 9 will be raised if the file can't be written to.

        Arguments:
            ones_fill - Set to True if spare bits should be filled with
                        ones. (default=False)

        Return Value(s):
            None.

        Side Effects:
            Any buffered bits will be written to an output stream.
            _output_buffer will be zeroed.

        Exceptions Raised:
            ValueError - Raised if the stream is not opened.
            IOError 9 - Raised if the file cannot be written to.

        """

        self._verify_opened()

        if not self._is_writable():
            raise IOError(errno.EBADF, 'Bad file descriptor')

        if self._output_buffer[0] == 0:
            return 0

        # There must be unwritten bits.  Write them out.
        return_value = self._output_buffer[0]
        bits = self._output_buffer[1] << (8 - self._output_buffer[0])
        bits = bits & 0xFF

        if ones_fill:
            bits = bits | (0xFF >> self._output_buffer[0])

        self._stream.write(chr(bits))
        self._stream.flush()
        self._output_buffer = [0, 0]

        return return_value

    def get_char(self):
        """Read the next character from an input stream.

        This method reads one character (byte) from the input stream.

        Arguments:
            None.

        Return Value(s):
            The next character (byte) form an open input stream.

        Side Effects:
            One byte is read from the input stream.
            _input_buffer is updated appropriately.

        Exceptions Raised:
            ValueError - Raised if the stream is not opened.
            IOError 9 - Raised if the file cannot read from.
            EOFError - An attempt is made to read past the end of the
                       file.

        """

        self._verify_opened()

        if not self._is_readable():
            raise IOError(errno.EBADF, 'Bad file descriptor')

        return_value = self._stream.read(1)

        if return_value == '':
            raise EOFError
        else:
            return_value = ord(return_value)

        if self._input_buffer[0] == 0:
            # We can just get the byte the from file.
            return chr(return_value)

        # We have some buffered bits to return too.
        tmp = return_value >> self._input_buffer[0]
        tmp = tmp | self._input_buffer[1] << (8 - self._input_buffer[0])

        # Put remaining bits in buffer.  Count shouldn't change.
        self._input_buffer[1] = return_value & 0xFF
        return_value = tmp & 0xFF

        return chr(return_value)

    def put_char(self, c):
        """Write a character to an output stream.

        This method writes one character (byte) to the output stream.

        Arguments:
            c - The character to be written.  If c is not a string
                instance, an attempt will be made to convert it to
                a chr.

        Return Value(s):
            The character that was written.

        Side Effects:
            One byte is written to the output stream.
            _output_buffer is updated appropriately.

        Exceptions Raised:
            ValueError - Raised if the stream is not opened.
            IOError 9 - Raised if the file cannot written to.

        """

        self._verify_opened()

        if not self._is_writable():
            raise IOError(errno.EBADF, 'Bad file descriptor')

        if self._output_buffer[0] == 0:
            # We can just get the byte the from file.
            if not isinstance(c, basestring):
                c = chr(c)      # Make c a char for writing
            else:
                c = c[0]        # Use first chr if c is more than 1 char.
            self._stream.write(c)
            return c

        if isinstance(c, basestring):
            c = ord(c[0])       # Make sure we have a byte value.

        c = c & 0xFF
        tmp = c >> self._output_buffer[0]
        tmp = tmp | self._output_buffer[1] << (8 - self._output_buffer[0])
        tmp = tmp & 0xFF
        self._stream.write(chr(tmp))

        # Put remaining in buffer. count shouldn't change.
        self._output_buffer[1] = c

        return chr(c)

    def get_bit(self):
        """Read the next bit from an input stream.

        This method reads one bit from the input stream.

        Arguments:
            None.

        Return Value(s):
            The next bit form an open input stream.

        Side Effects:
            One byte is read from the input stream if the bit buffer is
            currently empty.
            _input_buffer is updated appropriately.

        Exceptions Raised:
            ValueError - Raised if the stream is not opened.
            IOError 9 - Raised if the file cannot read from.
            EOFError - An attempt is made to read past the end of the
                       file.

        """

        self._verify_opened()

        if not self._is_readable():
            raise IOError(errno.EBADF, 'Bad file descriptor')

        if self._input_buffer[0] == 0:
            # The buffer is empty, read another character.
            self._input_buffer[1] = self._stream.read(1)

            if self._input_buffer[1] == '':
                raise EOFError
            else:
                self._input_buffer[1] = ord(self._input_buffer[1])

            self._input_buffer[0] = 8

        # The bit to return is msb in buffer.
        self._input_buffer[0] = self._input_buffer[0] - 1
        return_value = self._input_buffer[1] >> self._input_buffer[0]

        return return_value & 0x01

    def put_bit(self, bit):
        """Write a bit to an output stream.

        This method writes one character (byte) to the output stream.

        Arguments:
            bit - bit to be written.  If bit evaluates to True a 1 will
                  be written.  Otherwise a zero will be written.

        Return Value(s):
            The value of the bit that was written.

        Side Effects:
            One byte may be written to the output stream.
            _output_buffer is updated appropriately.

        Exceptions Raised:
            ValueError - Raised if the stream is not opened.
            IOError 9 - Raised if the file cannot written to.

        """

        self._verify_opened()

        if not self._is_writable():
            raise IOError(errno.EBADF, 'Bad file descriptor')

        self._output_buffer[0] = self._output_buffer[0] + 1
        self._output_buffer[1] = (self._output_buffer[1] << 1) & 0xFF

        if bit:
            self._output_buffer[1] |= 1
            bit = 1
        else:
            bit = 0

        # Write bit the buffer if we have 8 bits.
        if self._output_buffer[0] == 8:
            self._stream.write(chr(self._output_buffer[1]))
            self._output_buffer = [0, 0]

        return bit

    def get_bits_mtol(self, count):
        """Read bits from an input stream MSByte to LSByte.

        This method reads the specified number of bits from the input
        stream.  The bits are returned in an integer, filling it MSByte
        to LSByte.

        Arguments:
            count - the number of bits to be read.

        Return Value(s):
            An integer object containing the bits form an open input
            stream.  The bits are stored in the integer MSByte to
            LSByte.  If an integral number of bytes are not read, the
            bits in the last byte will be left justified (msbits).

        Side Effects:
            The specified number of bits will be read from the input
            stream and/or bit buffer.
            _input_buffer is updated appropriately.

        Exceptions Raised:
            ValueError - Raised if the stream is not opened.
            IOError 9 - Raised if the file cannot read from.
            EOFError - An attempt is made to read past the end of the
                       file.

        """

        self._verify_opened()

        if not self._is_readable():
            raise IOError(errno.EBADF, 'Bad file descriptor')

        remaining = count
        as_str = ''

        # Read whole bytes.
        while remaining >= 8:
            return_value = self.get_char()
            as_str = as_str + return_value
            remaining = remaining - 8

        if remaining != 0:
            # Read all remaining bits.
            last = 0
            shifts = 8 - remaining

            while remaining > 0:
                return_value = self.get_bit()
                last = last << 1
                last = last | (return_value & 0x01)
                remaining = remaining - 1

            # Shift the final bits into position and add to str
            last = (last << shifts) & 0xFF
            as_str = as_str + chr(last)

        # Make integer out of as_str.
        return_value = str_to_int(as_str)
        return return_value

    def put_bits_mtol(self, bits, count):
        """Write bits to an output stream MSByte to LSByte.

        This method writes the specified number of bits to the output
        stream.  Bits are read from an integer object containing the
        bits MSByte to LSByte.  The bytes are copied to the open output
        stream in the order that they are read.  If an integral number
        of bytes are not specified, the ms bits in the last byte will be
        written.

        Arguments:
            bits - an object containing the bits to be written.
            count - the number of bits to be written.

        Return Value(s):
            The number of bits written.

        Side Effects:
            The specified number of bits will be written to the output
            stream and/or bit buffer.
            _output_buffer is updated appropriately.

        Exceptions Raised:
            ValueError - Raised if the stream is not opened.
            IOError 9 - Raised if the file cannot written to.

        """

        self._verify_opened()

        if not self._is_writable():
            raise IOError(errno.EBADF, 'Bad file descriptor')

        remaining = count

        if not isinstance(bits, basestring):
            as_str = int_to_str(bits, (count + 7) / 8)
        else:
            as_str = bits

        # Write whole bytes.
        while remaining >= 8:
            return_value = self.put_char(as_str[0])
            remaining -= 8
            as_str = as_str[1:]

        if remaining != 0:
            # Write the remaining bits.
            tmp = ord(as_str)

            while remaining > 0:
                self.put_bit(tmp & 0x80)
                tmp = (tmp << 1) & 0xFF
                remaining = remaining - 1

        return count

    def get_bits_ltom(self, count):
        """Read bits from an input stream LSByte to MSByte.

        This method reads the specified number of bits from the input
        stream.  The bits are returned in an integer, filling it LSByte
        to MSByte.

        Arguments:
            count - the number of bits to be read.

        Return Value(s):
            An integer object containing the bits form an open input
            stream.  The bits are stored in the integer LSByte to
            MSByte.  If an integral number of bytes are not read, the
            bits in the last byte will be right justified (lsbits).

        Side Effects:
            The specified number of bits will be read from the input
            stream and/or bit buffer.
            _input_buffer is updated appropriately.

        Exceptions Raised:
            ValueError - Raised if the stream is not opened.
            IOError 9 - Raised if the file cannot read from.
            EOFError - An attempt is made to read past the end of the
                       file.

        """

        self._verify_opened()

        if not self._is_readable():
            raise IOError(errno.EBADF, 'Bad file descriptor')

        remaining = count
        as_str = ''

        # Read whole bytes.
        while remaining >= 8:
            return_value = self.get_char()
            as_str = return_value + as_str
            remaining = remaining - 8

        if remaining != 0:
            # Read all remaining bits.
            last = 0

            while remaining > 0:
                return_value = self.get_bit()
                last = last << 1
                if return_value:
                    last = last | 0x01
                remaining = remaining - 1

            as_str = chr(last) + as_str

        # Make integer out of as_str.
        return_value = str_to_int(as_str)
        return return_value

    def put_bits_ltom(self, bits, count):
        """Write bits to an output stream LSByte to MSByte.

        This method writes the specified number of bits to the output
        stream.  Bits are read from an integer object containing the
        bits LSByte to MSByte.  The bytes are copied to the open output
        stream in the order that they are read.  If an integral number
        of bytes are not specified, the ls bits in the last byte will be
        written.

        Arguments:
            bits - an object containing the bits to be written.
            count - the number of bits to be written.

        Return Value(s):
            The number of bits written.

        Side Effects:
            The specified number of bits will be written to the output
            stream and/or bit buffer.
            _output_buffer is updated appropriately.

        Exceptions Raised:
            ValueError - Raised if the stream is not opened.
            IOError 9 - Raised if the file cannot written to.

        """

        self._verify_opened()

        if not self._is_writable():
            raise IOError(errno.EBADF, 'Bad file descriptor')

        remaining = count

        if not isinstance(bits, basestring):
            as_str = int_to_str(bits, (count + 7) / 8)
        else:
            as_str = bits

        # Write whole bytes.
        while remaining >= 8:
            return_value = self.put_char(as_str[-1])
            remaining -= 8
            as_str = as_str[0:-1]

        if remaining != 0:
            # Write the remaining bits.
            tmp = ord(as_str[0])
            tmp = tmp << (8 - remaining)
            while remaining > 0:
                self.put_bit(tmp & 0x80)
                tmp = tmp << 1
                remaining = remaining - 1

        return count
