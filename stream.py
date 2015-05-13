import json

from PySide.QtCore import QProcess, Qt
from PySide.QtGui import QColor, QFont, QPixmap, QWidget, QPainter, QLabel

class ImageWidget(QLabel):

	def __init__(self, imagePath, parent):
		super(ImageWidget, self).__init__(parent)
		picture = QPixmap(imagePath)
		self.setAlignment(Qt.AlignCenter)
		self.setPixmap(picture)

class MovieWidget(QWidget):

	def __init__(self, moviePath, parent):
		super(MovieWidget, self).__init__(parent)
		movie = QMovie(moviePath)
		self.setMovie(movie)
		movie.start()

class Stream:

	ALL_STREAMS = []

	def __init__( self, arguments ):

		self.arguments = arguments


	def start( self, messageElement ):

		Stream.clear_streams()

		process = QProcess()

		self.process = process
		self.messageElement = messageElement

		process.setProcessChannelMode( QProcess.MergedChannels )
		process.start( 'livestreamer', self.arguments )
		process.readyReadStandardOutput.connect( self.show_messages )

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

		#~ tableWidgetItem.setForeground(QColor(0,0,0))
		#~ tableWidgetItem.setText( 'Checking..' )
		itemWidget = self.table_widget_item
		tableWidget = itemWidget.tableWidget()
		tableWidget.setCellWidget( itemWidget.row(), itemWidget.column(), ImageWidget('icons/loading_16.png', tableWidget) )

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
			tableWidget.setCellWidget( itemWidget.row(), itemWidget.column(), ImageWidget('icons/offline_16.png', tableWidget) )
			#~ itemWidget.setForeground(QColor(255,0,0))
			onlineStatus = 'Offline'
		else:
			tableWidget.setCellWidget( itemWidget.row(), itemWidget.column(), ImageWidget('icons/online_16.png', tableWidget) )
			#~ itemWidget.setForeground(QColor(0,200,0))
			onlineStatus = 'Online'



		#~ itemWidget.setText( onlineStatus )


	def show_messages( self ):

		outputBytes = self.process.readAll().data()

		outputUnicode = outputBytes.decode( 'utf-8' )

		self.messageElement.append( outputUnicode )



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