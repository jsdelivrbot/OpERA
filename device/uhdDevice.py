## @package device

from gnuradio import uhd
from abstractDevice import AbstractDevice

## Base class to UHDSource and UHDSink
class UHDBase(AbstractDevice):

	## CTOR.
	# @param uhd UHD Device: uhd.usrp_source or uhd.usrp_sink.
	def __init__(self, uhd):
		AbstractDevice.__init__(self)
		self._uhd = uhd

	## Getter for the UHD device.
	# @return The uhd_source/sink device.
	@property
	def uhd(self):
		return self._uhd

# center_freq property
	## @abstract
	def _get_center_freq(self):
		return self.uhd.get_center_freq()

	## @abstract
	def _set_center_freq(self, center_freq):
		self.uhd.set_center_freq( center_freq )

# samp_rate property
	def _get_samp_rate(self):
		return self.uhd.get_samp_rate()

	def _set_samp_rate(self, samp_rate):
		self.uhd.set_samp_rate( samp_rate )

# gain property
	def _get_gain(self):
		return self.uhd.get_gain()

	def _set_gain(self, gain):
		self.uhd.set_gain( gain )


## Wrapper for uhd.usrp_source device.
# Always utilizes the 'RX2' antenna.
class UHDSource(UHDBase):

	## CTOR.
	# @param  device_addr USRP IP address.
	# @param stream_args USRP stream arguments.
	def __init__(
			self,
			device_addr = '',
			stream_args = uhd.stream_args('fc32')
			):

		# Only creates the base class passing a uhd.usrp_source
		UHDBase.__init__(
				self,
				uhd = uhd.usrp_source(
					device_addr = device_addr,
					stream_args = stream_args)
				)

		self.uhd.set_antenna('RX2', 0)

## Wrapper for uhd.usrp_sink device.
# Always utilize the TX/RX antenna.
class UHDSink(UHDBase):

	## CTOR.
	# @param  device_addr USRP IP address.
	# @param stream_args USRP stream arguments.
	def __init__(
			self,
			device_addr = '',
			stream_args = uhd.stream_args('fc32')
			):

		# Only creates the base class passing a uhd.usrp_sink
		UHDBase.__init__(
				self,
				uhd = uhd.usrp_sink(
					device_addr = device_addr,
					stream_args = stream_args)
				)

		self.uhd.set_antenna('TX/RX', 0)


