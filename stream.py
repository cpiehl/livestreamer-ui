import json, os

from PySide.QtCore import QProcess, Qt
from PySide.QtGui import *

# changes relative into full path so we can run from anywhere
def fullpath( filename ):
	return os.path.join(os.path.dirname(__file__), filename)


class ImageWidget(QLabel):

	def __init__(self, imagePath, parent):
		super(ImageWidget, self).__init__(parent)
		self.imagePath = imagePath
		picture = QPixmap(self.imagePath)
		self.setAlignment(Qt.AlignCenter)
		self.setPixmap(picture)

	def filename( self ):
		return self.imagePath


class MovieWidget(QLabel):

	def __init__(self, moviePath, parent):
		super(MovieWidget, self).__init__(parent)
		self.moviePath = moviePath
		movie = QMovie(self.moviePath)
		self.setAlignment(Qt.AlignCenter)
		self.setMovie(movie)
		movie.start()

	def filename( self ):
		return self.moviePath


class Stream:

	ALL_STREAMS = []

	def __init__( self, arguments ):

		self.arguments = arguments


	def start( self, messageElement, tableWidgetItem ):

		Stream.clear_streams()

		process = QProcess()
		self.process = process
		self.messageElement = messageElement

		row = tableWidgetItem.row()
		tableWidget = tableWidgetItem.tableWidget()
		tableWidget.setCellWidget( tableWidgetItem.row(), 0, ImageWidget( fullpath( 'icons/play_16.png' ), tableWidget) )
		tableWidgetItem = tableWidget.item( row, 0 )

		process.setProcessChannelMode( QProcess.MergedChannels )
		process.start( 'livestreamer', self.arguments )
		process.readyReadStandardOutput.connect( self.show_messages )
		process.finished.connect( lambda: self.is_online( tableWidgetItem ) )

		Stream.ALL_STREAMS.append( self )


	def is_online( self, tableWidgetItem ):

		Stream.clear_streams()
		process = QProcess()
		self.process = process
		self.table_widget_item = tableWidgetItem

		arguments = [ '--json' ] + self.arguments

		process.setProcessChannelMode( QProcess.MergedChannels )
		process.start( 'livestreamer', arguments )
		process.readyReadStandardOutput.connect( self.is_online_callback )

		itemWidget = self.table_widget_item
		tableWidget = itemWidget.tableWidget()
		tableWidget.setCellWidget( itemWidget.row(), 0, MovieWidget( fullpath( 'icons/loading_16.gif' ), tableWidget) )

		Stream.ALL_STREAMS.append( self )


	def is_online_callback( self ):

		outputBytes = self.process.readAll().data()
		outputUnicode = outputBytes.decode( 'utf-8' )

		try:
			outputObject = json.loads( outputUnicode )
		except ValueError as errorMessage:
			print( errorMessage )
			return

		itemWidget = self.table_widget_item
		tableWidget = itemWidget.tableWidget()

		if outputObject.get( 'error' ):
			tableWidget.setCellWidget( itemWidget.row(), 0, ImageWidget( fullpath( 'icons/offline_16.png' ), tableWidget) )
			onlineStatus = 'Offline'
		else:
			tableWidget.setCellWidget( itemWidget.row(), 0, ImageWidget( fullpath( 'icons/online_16.png' ), tableWidget) )
			onlineStatus = 'Online'


	def show_messages( self ):

		outputBytes = self.process.readAll().data()
		outputUnicode = outputBytes.decode( 'utf-8' )
		self.messageElement.append( outputUnicode )
		print (outputUnicode)


	@staticmethod
	def clear_streams():

		"""
			Remove the streams that have ended (process is not running anymore) from the list that contains all the stream objects
		"""

		streams = []

		for stream in Stream.ALL_STREAMS:
			if stream.process.state() != QProcess.NotRunning:
				streams.append( stream )

		Stream.ALL_STREAMS = streams

