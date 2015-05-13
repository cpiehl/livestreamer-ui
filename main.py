#!/usr/bin/env python3

import sys
import json

#~ from PySide.QtGui import QApplication, QLabel, QPushButton, QLineEdit, QWidget, QTextEdit, QGridLayout, QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView, QMenu
from PySide.QtGui import *
from PySide.QtCore import Qt

from stream import Stream

	# FileNotFoundError is python3.3+ only
try:
	TryFileNotFound = FileNotFoundError

except NameError:
	TryFileNotFound = IOError

class LiveStreamer( QWidget ):

	def __init__( self ):
		super(LiveStreamer, self).__init__()

		url = QLineEdit()
		urlLabel = QLabel( 'Url' )
		messages = QTextEdit()
		messagesLabel = QLabel( 'Messages' )
		links = QTableWidget( 0, 2 )
		clearMessages = QPushButton( 'Clear Messages' )
		checkIfOnline = QPushButton( QIcon( QPixmap( 'icons/reload_16.png' ) ), '' )
		addLink = QPushButton( QIcon( QPixmap( 'icons/add_16.png' ) ), '' )

			# make it pretty
		links.horizontalHeader().hide()
		links.verticalHeader().hide()
		links.setShowGrid(False)
		links.setSelectionBehavior(QAbstractItemView.SelectRows)
		checkIfOnline.setMaximumWidth(32)
		addLink.setMaximumWidth(32)

			# add right click context menu
		links.setContextMenuPolicy(Qt.CustomContextMenu)
		links.customContextMenuRequested.connect(self.links_context_menu)

		#~ linksLabel.setMaximumHeight( 20 )

		messages.setReadOnly( True )

		links.setHorizontalHeaderLabels( [ 'Status', 'Url' ] )
		links.horizontalHeader().setResizeMode( 0, QHeaderView.ResizeToContents )
		links.horizontalHeader().setResizeMode( 1, QHeaderView.Stretch )

			# set the events

		url.returnPressed.connect( self.select_stream_from_entry )
		links.itemDoubleClicked.connect( self.select_stream_from_link )
		clearMessages.clicked.connect( self.clear_messages )
		checkIfOnline.clicked.connect( self.check_if_online )
		addLink.clicked.connect( self.add_link_dialog )

			# set the layouts
		mainLayout = QGridLayout()

			# first row  (links widget occupies 3 rows and 3 columns)
		mainLayout.addWidget( links, 0, 0, 3, 3 )   # spans 3 columns

			# fourth row
		mainLayout.addWidget( checkIfOnline, 3, 1 )
		mainLayout.addWidget( addLink, 3, 2 )


		window = QWidget()

		window.setLayout( mainLayout )
		window.setWindowTitle( 'Live Streamer' )
		window.resize( 400, 350 )
		window.show()

		self.url_ui = url
		self.messages_ui = messages
		self.links_ui = links
		self.window_ui = window

		self.links = set()

	def links_context_menu( self, pos ):
		menu = QMenu()
		playAction = menu.addAction( QIcon( QPixmap( 'icons/play_16.png' ) ), "Watch" )
		reloadAction = menu.addAction( QIcon( QPixmap( 'icons/reload_16.png' ) ), "Reload" )
		removeAction = menu.addAction( QIcon( QPixmap( 'icons/remove_16.png' ) ), "Remove" )
		action = menu.exec_( self.links_ui.mapToGlobal( pos ) )
		if action == playAction:
			self.select_stream_from_link( self.links_ui.currentItem() )
		elif action == reloadAction:
			self.reload_selected_link()
		elif action == removeAction:
			self.remove_selected_link()

	def add_link_dialog( self ):
		text, ok = QInputDialog.getText( self, 'Add Link', 'URL:' )

		if ok:
			self.add_link( text )

	def select_stream_from_entry( self ):

		"""
			Gets the values from the ui elements, and executes the program in json mode, to determine if the values are valid
		"""
		url = self.url_ui.text()
		split_url = url.split()

		self.messages_ui.append( 'Trying to open stream: {}'.format( url ) )

		stream = Stream( split_url )

		stream.start( self.messages_ui )



	def select_stream_from_link( self, tableWidgetItem ):

		row = tableWidgetItem.row()

		urlItem = self.links_ui.item( row, 1 )  # the url is in the first column

		url = urlItem.text()

		split_url = url.split()

		self.messages_ui.append( 'Trying to open stream: {}'.format( url ) )


		stream = Stream( split_url )

		stream.start( self.messages_ui )



	def clear_messages( self ):

		self.messages_ui.setText( '' )


	def add_link( self, url ):

		"""
			Adds a link to the link widget.

			Only adds if its not already present.
		"""

		if url not in self.links:

			self.links.add( url )


			rowCounts = self.links_ui.rowCount()
			nextRow = rowCounts + 1
			nextPosition = rowCounts    # row count is the length, but position is zero-based

			self.links_ui.setRowCount( nextRow )

			urlEntry = QTableWidgetItem( url )
			statusEntry = QTableWidgetItem( '' )

			statusEntry.setTextAlignment( Qt.AlignCenter )

			statusEntry.setFlags( statusEntry.flags() & ~Qt.ItemIsEditable ) # not editable
			urlEntry.setFlags( urlEntry.flags() & ~Qt.ItemIsEditable ) # not editable

			self.links_ui.setItem( nextPosition, 0, statusEntry )
			self.links_ui.setItem( nextPosition, 1, urlEntry )


				# check if online
			stream = Stream( url.split() )

			stream.is_online( statusEntry )



	def add_selected_link( self ):

		url = self.url_ui.text()

		if url:

			self.add_link( url )


	def remove_selected_link( self ):

		selectedItem = self.links_ui.currentItem()

		if selectedItem:

			self.links.remove( selectedItem.text() )

			currentRow = self.links_ui.currentRow()
			self.links_ui.removeRow( currentRow )


	def reload_selected_link( self ):

		statusItem = self.links_ui.item( self.links_ui.currentRow(), 0 )
		urlItem = self.links_ui.item( self.links_ui.currentRow(), 1 )

		url = urlItem.text()
		splitUrl = url.split()
		stream = Stream( splitUrl )

		stream.is_online( statusItem )


	def check_if_online( self ):

		"""
			Check if any of the streams saved is online
		"""

		for row in range( self.links_ui.rowCount() ):

			statusItem = self.links_ui.item( row, 0 )
			urlItem = self.links_ui.item( row, 1 )

			url = urlItem.text()

			splitUrl = url.split()

			stream = Stream( splitUrl )

			stream.is_online( statusItem )





	def save( self ):

		"""
			Save any data to a file (the links/etc)
		"""

			# json doesn't have sets, so convert to a list
		linksList = list( self.links )

		saveJsonText = json.dumps( linksList )

		with open( 'data.txt', 'w', encoding= 'utf-8' ) as f:
			f.write( saveJsonText )


	def load( self ):

		"""
			Load any saved data
		"""

		try:
			file = open( 'data.txt', 'r', encoding= 'utf-8' )

		except TryFileNotFound:
			return


		linksList = json.loads( file.read() )

		file.close()


		for link in linksList:
			self.add_link( link )


		self.check_if_online()



if __name__ == '__main__':

	app = QApplication( sys.argv )

	streamer = LiveStreamer()

	streamer.load()

	app.aboutToQuit.connect( streamer.save )

	app.exec_()



