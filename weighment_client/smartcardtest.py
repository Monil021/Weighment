# # # # import cv2
# # # # from datetime import datetime

# # # # def capture_photo(camera_url, save_path):
# # # #     # Open the RTSP stream
# # # #     cap = cv2.VideoCapture(camera_url)

# # # #     # Check if the camera opened successfully
# # # #     if not cap.isOpened():
# # # #         print("Error: Could not open camera.")
# # # #         return

# # # #     try:
# # # #         # Capture a frame
# # # #         ret, frame = cap.read()

# # # #         if ret:
# # # #             # Generate a unique filename based on current datetime
# # # #             current_datetime = datetime.now().strftime("%Y%m%d%H%M%S")
# # # #             filename = f"{save_path}/rohan_{current_datetime}.jpg"

# # # #             # Save the captured frame as an image
# # # #             cv2.imwrite(filename, frame)
# # # #             print(f"Photo captured and saved as: {filename}")

# # # #         else:
# # # #             print("Error: Failed to capture frame from the camera.")

# # # #     except Exception as e:
# # # #         print(f"Error: {e}")

# # # #     finally:
# # # #         # Release the camera
# # # #         cap.release()

# # # # if __name__ == "__main__":
# # # #     # Replace 'rtsp://admin:password123@12.0.0.169/stream' with your camera URL
# # # #     camera_url = 'rtsp://admin:password123@12.0.0.169/stream'
    
# # # #     # Specify the directory where you want to save the photo
# # # #     save_path = '.'  # Change this to your desired directory

# # # #     # Capture photo and save it
# # # #     capture_photo(camera_url, save_path)


# # # # import cv2

# # # # camera_url = 'rtsp://admin:password123@12.0.0.169/stream'
# # # # cap = cv2.VideoCapture(camera_url)

# # # # # Set the desired width and height
# # # # new_width = 640
# # # # new_height = 480

# # # # while True:
# # # #     ret, frame = cap.read()

# # # #     if not ret:
# # # #         print("Error reading frame")
# # # #         break

# # # #     # Resize the frame
# # # #     frame = cv2.resize(frame, (new_width, new_height))

# # # #     cv2.imshow('Camera Feed', frame)

# # # #     if cv2.waitKey(1) & 0xFF == ord('q'):
# # # #         break

# # # # cap.release()
# # # # cv2.destroyAllWindows()


# import subprocess
# import time
# import cv2
# import serial
# # from weighment_client.weighment_client_utils import execute_terminal_commands_for_button_or_weighbridge, get_serial_port

# # Dictionary containing camera URLs
# camera_urls = {
#     'camera1': 'rtsp://admin:password123@12.0.0.169/stream1',
#     # 'camera2': 'rtsp://admin:password123@12.0.0.169/stream2',
#     # 'camera3': 'rtsp://admin:password123@12.0.0.169/stream3'
#     # Add more camera URLs as needed
# }

# # # Dictionary to store capture objects
# # captures = {}

# # # Set the desired width and height for the displayed frames
# # new_width = 640
# # new_height = 480

# # # Open connections to the cameras
# # for cam_name, cam_url in camera_urls.items():
# #     captures[cam_name] = cv2.VideoCapture(cam_url)

# # # Display frames from each camera in separate windows
# # while True:
# #     for cam_name, cap in captures.items():
# #         ret, frame = cap.read()

# #         if not ret:
# #             print(f"Error reading frame from {cam_name}")
# #             continue

# #         # Resize the frame
# #         frame = cv2.resize(frame, (new_width, new_height))

# #         cv2.imshow(cam_name, frame)

# #     if cv2.waitKey(1) & 0xFF == ord('q'):
# #         break

# # # Release capture objects and close windows
# # for cap in captures.values():
# #     cap.release()
# # cv2.destroyAllWindows()

# # # from smartcard.scard import *
# # # import smartcard.util
# # # from weighment_client.weighment_client_utils import play_audio

# # # srTreeATR = [0x3B, 0x77, 0x94, 0x00, 0x00, 0x82, 0x30, 0x00, 0x13, 0x6C, 0x9F, 0x22]
# # # srTreeMask = [0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF]

# # # def printstate(state):
# # #     reader, eventstate, atr = state
# # #     print(reader + " " + smartcard.util.toHexString(atr, smartcard.util.HEX))
# # #     if eventstate & SCARD_STATE_ATRMATCH:
# # #         print('\tCard found')
# # #     if eventstate & SCARD_STATE_UNAWARE:
# # #         print('\tState unaware')
# # #     if eventstate & SCARD_STATE_IGNORE:
# # #         print('\tIgnore reader')
# # #     if eventstate & SCARD_STATE_UNAVAILABLE:
# # #         print('\tReader unavailable')
# # #     if eventstate & SCARD_STATE_EMPTY:
# # #         print('\tReader empty')
# # #     if eventstate & SCARD_STATE_PRESENT:
# # #         print('\tCard present in reader')
# # #     if eventstate & SCARD_STATE_EXCLUSIVE:
# # #         print('\tCard allocated for exclusive use by another application')
# # #     if eventstate & SCARD_STATE_INUSE:
# # #         print('\tCard in use by another application but can be shared')
# # #     if eventstate & SCARD_STATE_MUTE:
# # #         print('\tCard is mute')
# # #     if eventstate & SCARD_STATE_CHANGED:
# # #         print('\tState changed')
# # #     if eventstate & SCARD_STATE_UNKNOWN:
# # #         print('\tState unknown')

# # # try:
# # #     hresult, hcontext = SCardEstablishContext(SCARD_SCOPE_USER)
# # #     if hresult != SCARD_S_SUCCESS:
# # #         raise error('Failed to establish context: ' + SCardGetErrorMessage(hresult))
# # #     print('Context established!')

# # #     try:
# # #         while True:  # Continuously check for card insertion
# # #             hresult, readers = SCardListReaders(hcontext, [])
# # #             if hresult != SCARD_S_SUCCESS:
# # #                 raise error('Failed to list readers: ' + SCardGetErrorMessage(hresult))
# # #             print('PCSC Readers:', readers)

# # #             readerstates = []
# # #             for i in range(len(readers)):
# # #                 readerstates += [(readers[i], SCARD_STATE_UNAWARE)]

# # #             print('----- Current reader and card states are: -------')
# # #             hresult, newstates = SCardGetStatusChange(hcontext, 0, readerstates)
# # #             for i in newstates:
# # #                 printstate(i)

# # #             if not any(state[1] & SCARD_STATE_PRESENT for state in newstates):
# # #                 play_audio(audio_profile="Please put your card on the machine")

# # #             print('----- Please insert or remove a card ------------')

# # #             hresult, newstates = SCardGetStatusChange(hcontext, INFINITE, newstates)

# # #             print('----- New reader and card states are: -----------')
# # #             for i in newstates:
# # #                 printstate(i)

# # #     finally:
# # #         hresult = SCardReleaseContext(hcontext)
# # #         if hresult != SCARD_S_SUCCESS:
# # #             raise error('Failed to release context: ' + SCardGetErrorMessage(hresult))
# # #         print('Released context.')

# # #     import sys
# # #     if 'win32' == sys.platform:
# # #         print('press Enter to continue')
# # #         sys.stdin.read(1)

# # # except error as e:
# # #     print(e)


# # # # srTreeATR = \
# # # #     [0x3B, 0x77, 0x94, 0x00, 0x00, 0x82, 0x30, 0x00, 0x13, 0x6C, 0x9F, 0x22]
# # # # srTreeMask = \
# # # #     [0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF]


# # # # def printstate(state):
# # # #     reader, eventstate, atr = state
# # # #     print(reader + " " + smartcard.util.toHexString(atr, smartcard.util.HEX))
# # # #     if eventstate & SCARD_STATE_ATRMATCH:
# # # #         print('\tCard found')
# # # #     if eventstate & SCARD_STATE_UNAWARE:
# # # #         print('\tState unware')
# # # #     if eventstate & SCARD_STATE_IGNORE:
# # # #         print('\tIgnore reader')
# # # #     if eventstate & SCARD_STATE_UNAVAILABLE:
# # # #         print('\tReader unavailable')
# # # #     if eventstate & SCARD_STATE_EMPTY:
# # # #         print('\tReader empty')
        
# # # #     if eventstate & SCARD_STATE_PRESENT:
# # # #         print('\tCard present in reader')
# # # #     if eventstate & SCARD_STATE_EXCLUSIVE:
# # # #         print('\tCard allocated for exclusive use by another application')
# # # #     if eventstate & SCARD_STATE_INUSE:
# # # #         print('\tCard in used by another application but can be shared')
# # # #     if eventstate & SCARD_STATE_MUTE:
# # # #         print('\tCard is mute')
# # # #     if eventstate & SCARD_STATE_CHANGED:
# # # #         print('\tState changed')
# # # #     if eventstate & SCARD_STATE_UNKNOWN:
# # # #         print('\tState unknowned')


# # # # try:
# # # #     hresult, hcontext = SCardEstablishContext(SCARD_SCOPE_USER)
# # # #     if hresult != SCARD_S_SUCCESS:
# # # #         raise error(
# # # #             'Failed to establish context: ' +
# # # #             SCardGetErrorMessage(hresult))
# # # #     print('Context established!')

# # # #     try:
# # # #         hresult, readers = SCardListReaders(hcontext, [])
# # # #         if hresult != SCARD_S_SUCCESS:
# # # #             raise error(
# # # #                 'Failed to list readers: ' +
# # # #                 SCardGetErrorMessage(hresult))
# # # #         print('PCSC Readers:', readers)

# # # #         readerstates = []
# # # #         for i in range(len(readers)):
# # # #             readerstates += [(readers[i], SCARD_STATE_UNAWARE)]

# # # #         print('----- Current reader and card states are: -------')
# # # #         hresult, newstates = SCardGetStatusChange(hcontext, 0, readerstates)
# # # #         for i in newstates:
# # # #             printstate(i)

# # # #         print('----- Please insert or remove a card ------------')
# # # #         hresult, newstates = SCardGetStatusChange(
# # # #                                 hcontext,
# # # #                                 INFINITE,
# # # #                                 newstates)

# # # #         print('----- New reader and card states are: -----------')
# # # #         for i in newstates:
# # # #             printstate(i)

# # # #     finally:
# # # #         hresult = SCardReleaseContext(hcontext)
# # # #         if hresult != SCARD_S_SUCCESS:
# # # #             raise error(
# # # #                 'Failed to release context: ' +
# # # #                 SCardGetErrorMessage(hresult))
# # # #         print('Released context.')

# # # #     import sys
# # # #     if 'win32' == sys.platform:
# # # #         print('press Enter to continue')
# # # #         sys.stdin.read(1)

# # # # except error as e:
# # # #     print(e)

# # import frappe
# # from smartcard.scard import *
# # import smartcard.util
# # import os
# # import tempfile
# # from playsound import playsound

# # def insert_or_remove_card():
# #     srTreeATR = [0x3B, 0x77, 0x94, 0x00, 0x00, 0x82, 0x30, 0x00, 0x13, 0x6C, 0x9F, 0x22]
# #     srTreeMask = [0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF]

# #     def printstate(state):
# #         reader, eventstate, atr = state
# #         print(reader + " " + smartcard.util.toHexString(atr, smartcard.util.HEX))
#         # if eventstate & SCARD_STATE_ATRMATCH:
#         #     print('\tCard found')
# #         if eventstate & SCARD_STATE_UNAWARE:
# #             print('\tState unware')
# #         if eventstate & SCARD_STATE_IGNORE:
# #             print('\tIgnore reader')
# #         if eventstate & SCARD_STATE_UNAVAILABLE:
# #             print('\tReader unavailable')
# #         if eventstate & SCARD_STATE_EMPTY:
# #             print('\tReader empty')
# #         if eventstate & SCARD_STATE_PRESENT:
# #             print('\tCard present in reader')
# #         if eventstate & SCARD_STATE_EXCLUSIVE:
# #             print('\tCard allocated for exclusive use by another application')
# #         if eventstate & SCARD_STATE_INUSE:
# #             print('\tCard in used by another application but can be shared')
# #         if eventstate & SCARD_STATE_MUTE:
# #             print('\tCard is mute')
# #         if eventstate & SCARD_STATE_CHANGED:
# #             print('\tState changed')
# #         if eventstate & SCARD_STATE_UNKNOWN:
# #             print('\tState unknowned')

# #     try:
# #         hresult, hcontext = SCardEstablishContext(SCARD_SCOPE_USER)
# #         if hresult != SCARD_S_SUCCESS:
# #             raise error(
# #                 'Failed to establish context: ' +
# #                 SCardGetErrorMessage(hresult))
# #         print('Context established!')

# #         try:
# #             hresult, readers = SCardListReaders(hcontext, [])
# #             if hresult != SCARD_S_SUCCESS:
# #                 raise error(
# #                     'Failed to list readers: ' +
# #                     SCardGetErrorMessage(hresult))
# #             print('PCSC Readers:', readers)

# #             readerstates = []
# #             for i in range(len(readers)):
# #                 readerstates += [(readers[i], SCARD_STATE_UNAWARE)]

# #             print('----- Current reader and card states are: -------')
# #             hresult, newstates = SCardGetStatusChange(hcontext, 0, readerstates)
# #             for i in newstates:
# #                 printstate(i)

# #             print('----- Please insert or remove a card ------------')

# #             # Continuous check for card insertion
# #             while True:
# #                 hresult, newstates = SCardGetStatusChange(hcontext, INFINITE, newstates)
# #                 for i in newstates:
# #                     printstate(i)

# #                 # Check if card is inserted
# #                 if any(eventstate & SCARD_STATE_PRESENT for _, eventstate, _ in newstates):
# #                     break  # Exit the loop if card is inserted
# #                 else:
# #                     play_audio(audio_profile="Please put your card on machine")

# #         finally:
# #             hresult = SCardReleaseContext(hcontext)
# #             if hresult != SCARD_S_SUCCESS:
# #                 raise error(
# #                     'Failed to release context: ' +
# #                     SCardGetErrorMessage(hresult))
# #             print('Released context.')

# #     except error as e:
# #         print(e)

# # def play_audio(audio_profile):
# #     import os
# #     import tempfile
# #     from playsound import playsound

# #     if not audio_profile:
# #         frappe.throw("Please check the code you have entered...")
    
# #     audio = frappe.get_value("Audio File Details",{"audio_profile":audio_profile},["audio_file"])
# #     attachment = frappe.get_cached_doc("File",{"file_url":audio})

# #     temp_file_path = os.path.join(tempfile.gettempdir(),attachment.file_name)
# #     with open(temp_file_path, "wb") as temp_file:
# #         temp_file.write(attachment.get_content())

# #     playsound(temp_file_path)
# #     os.remove(temp_file_path)
# # insert_or_remove_card()


# # from gtts import gTTS
# # import os

# # def google_voice(text):
# #     tts = gTTS(text=text, lang="hi")
# #     filename = "voice.mp3"
# #     tts.save(filename)
# #     os.system("mpg321 " + filename)
# #     os.remove(filename)

# # # Example usage:
# # text_to_speak = "aapki khali gadi ka vajan, pandra Quintal, bis kilo huva. aapki bhari gadi ka vajan, pachas quintal, tiss kilo huva ? "
# # google_voice(text_to_speak)



# # from smartcard.scard import *
# # import smartcard.util

# # srTreeATR = \
# #     [0x3B, 0x77, 0x94, 0x00, 0x00, 0x82, 0x30, 0x00, 0x13, 0x6C, 0x9F, 0x22]
# # srTreeMask = \
# #     [0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF]


# # def printstate(state):
# #     reader, eventstate, atr = state
# #     print(reader + " " + smartcard.util.toHexString(atr, smartcard.util.HEX))
# #     if eventstate & SCARD_STATE_ATRMATCH:
# #         print('\tCard found')
# #     if eventstate & SCARD_STATE_UNAWARE:
# #         print('\tState unware')
# #     if eventstate & SCARD_STATE_IGNORE:
# #         print('\tIgnore reader')
# #     if eventstate & SCARD_STATE_UNAVAILABLE:
# #         print('\tReader unavailable')
# #     if eventstate & SCARD_STATE_EMPTY:
# #         print('\tReader empty')
# #     if eventstate & SCARD_STATE_PRESENT:
# #         print('\tCard present in reader')
# #     if eventstate & SCARD_STATE_EXCLUSIVE:
# #         print('\tCard allocated for exclusive use by another application')
# #     if eventstate & SCARD_STATE_INUSE:
# #         print('\tCard in used by another application but can be shared')
# #     if eventstate & SCARD_STATE_MUTE:
# #         print('\tCard is mute')
# #     if eventstate & SCARD_STATE_CHANGED:
# #         print('\tState changed')
# #     if eventstate & SCARD_STATE_UNKNOWN:
# #         print('\tState unknowned')


# # try:
# #     hresult, hcontext = SCardEstablishContext(SCARD_SCOPE_USER)
# #     if hresult != SCARD_S_SUCCESS:
# #         raise error(
# #             'Failed to establish context: ' +
# #             SCardGetErrorMessage(hresult))
# #     print('Context established!')

# #     try:
# #         hresult, readers = SCardListReaders(hcontext, [])
# #         if hresult != SCARD_S_SUCCESS:
# #             raise error(
# #                 'Failed to list readers: ' +
# #                 SCardGetErrorMessage(hresult))
# #         print('PCSC Readers:', readers)

# #         readerstates = []
# #         for i in range(len(readers)):
# #             readerstates += [(readers[i], SCARD_STATE_UNAWARE)]

# #         print('----- Current reader and card states are: -------')
# #         hresult, newstates = SCardGetStatusChange(hcontext, 0, readerstates)
# #         for i in newstates:
# #             printstate(i)

# #         print('----- Please insert or remove a card ------------')
# #         hresult, newstates = SCardGetStatusChange(
# #                                 hcontext,
# #                                 INFINITE,
# #                                 newstates)

# #         print('----- New reader and card states are: -----------')
# #         for i in newstates:
# #             printstate(i)

# #     finally:
# #         hresult = SCardReleaseContext(hcontext)
# #         if hresult != SCARD_S_SUCCESS:
# #             raise error(
# #                 'Failed to release context: ' +
# #                 SCardGetErrorMessage(hresult))
# #         print('Released context.')

# #     import sys
# #     if 'win32' == sys.platform:
# #         print('press Enter to continue')
# #         sys.stdin.read(1)

# # except error as e:
# #     print(e)


# # from smartcard.scard import *
# # import smartcard.util

# # def insert_or_remove_card():
# #     srTreeATR = \
# #         [0x3B, 0x77, 0x94, 0x00, 0x00, 0x82, 0x30, 0x00, 0x13, 0x6C, 0x9F, 0x22]
# #     srTreeMask = \
# #         [0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF]


# #     def printstate(state):
# #         reader, eventstate, atr = state
# #         print(reader + " " + smartcard.util.toHexString(atr, smartcard.util.HEX))
# #         if eventstate & SCARD_STATE_ATRMATCH:
# #             print('\tCard found')
# #             # play_audio(audio_profile="Please remove your card")
# #         if eventstate & SCARD_STATE_UNAWARE:
# #             print('\tState unware')
# #         if eventstate & SCARD_STATE_IGNORE:
# #             print('\tIgnore reader')
# #         if eventstate & SCARD_STATE_UNAVAILABLE:
# #             print('\tReader unavailable')
# #         if eventstate & SCARD_STATE_EMPTY:
# #             print('\tReader empty')
# #         if eventstate & SCARD_STATE_PRESENT:
# #             print('\tCard present in reader')
# #             # play_audio(audio_profile="Please remove your card")
# #         if eventstate & SCARD_STATE_EXCLUSIVE:
# #             print('\tCard allocated for exclusive use by another application')
# #         if eventstate & SCARD_STATE_INUSE:
# #             print('\tCard in used by another application but can be shared')
# #         if eventstate & SCARD_STATE_MUTE:
# #             print('\tCard is mute')
# #         if eventstate & SCARD_STATE_CHANGED:
# #             print('\tState changed')
# #         if eventstate & SCARD_STATE_UNKNOWN:
# #             print('\tState unknowned')


# #     try:
# #         hresult, hcontext = SCardEstablishContext(SCARD_SCOPE_USER)
# #         if hresult != SCARD_S_SUCCESS:
# #             raise error(
# #                 'Failed to establish context: ' +
# #                 SCardGetErrorMessage(hresult))
# #         print('Context established!')

# #         try:
# #             hresult, readers = SCardListReaders(hcontext, [])
# #             if hresult != SCARD_S_SUCCESS:
# #                 raise error(
# #                     'Failed to list readers: ' +
# #                     SCardGetErrorMessage(hresult))
# #             print('PCSC Readers:', readers)

# #             readerstates = []
# #             for i in range(len(readers)):
# #                 readerstates += [(readers[i], SCARD_STATE_UNAWARE)]

# #             print('----- Current reader and card states are: -------')
# #             hresult, newstates = SCardGetStatusChange(hcontext, 0, readerstates)
# #             for i in newstates:
# #                 printstate(i)
# #                 # play_audio(audio_profile="Please put your card on machine")

# #             print('----- Please insert or remove a card ------------')

# #             hresult, newstates = SCardGetStatusChange(
# #                                     hcontext,
# #                                     INFINITE,
# #                                     newstates)

# #             print('----- New reader and card states are: -----------')
# #             for i in newstates:
# #                 printstate(i)

# #         finally:
# #             hresult = SCardReleaseContext(hcontext)
# #             if hresult != SCARD_S_SUCCESS:
# #                 raise error(
# #                     'Failed to release context: ' +
# #                     SCardGetErrorMessage(hresult))
# #             print('Released context.')

# #         import sys
# #         if 'win32' == sys.platform:
# #             print('press Enter to continue')
# #             sys.stdin.read(1)

# #     except error as e:
# #         print(e)


# # from time import sleep

# # from smartcard.CardMonitoring import CardMonitor, CardObserver
# # from smartcard.util import toHexString


# # # a simple card observer that prints inserted/removed cards
# # class PrintObserver(CardObserver):
# #     """A simple card observer that is notified
# #     when cards are inserted/removed from the system and
# #     prints the list of cards
# #     """

# #     def update(self, observable, actions):
# #         (addedcards, removedcards) = actions
# #         for card in addedcards:
# #             print("+Inserted: ", toHexString(card.atr))
# #         for card in removedcards:
# #             print("-Removed: ", toHexString(card.atr))

# # if __name__ == '__main__':
# #     print("Insert or remove a smartcard in the system.")
# #     print("This program will exit in 10 seconds")
# #     print("")
# #     cardmonitor = CardMonitor()
# #     cardobserver = PrintObserver()
# #     cardmonitor.addObserver(cardobserver)

# #     sleep(10)

# #     # don't forget to remove observer, or the
# #     # monitor will poll forever...
# #     cardmonitor.deleteObserver(cardobserver)

# #     import sys
# #     if 'win32' == sys.platform:
# #         print('press Enter to continue')
# #         sys.stdin.read(1)


# # from time import sleep

# # from smartcard.CardMonitoring import CardMonitor, CardObserver
# # from smartcard.util import toHexString


# # # a simple card observer that prints inserted/removed cards
# # class PrintObserver(CardObserver):
# #     """A simple card observer that is notified
# #     when cards are inserted/removed from the system and
# #     prints the list of cards
# #     """

# #     def update(self, observable, actions):
# #         (addedcards, removedcards) = actions
# #         for card in addedcards:
# #             print("+Inserted: ", toHexString(card.atr))
# #         for card in removedcards:
# #             print("-Removed: ", toHexString(card.atr))

# # if __name__ == '__main__':
# #     print("Insert or remove a smartcard in the system.")
# #     print("This program will exit in 10 seconds")
# #     print("")
# #     cardmonitor = CardMonitor()
# #     print("88888888888888")
# #     cardobserver = PrintObserver()
# #     cardmonitor.addObserver(cardobserver)

# #     sleep(10)

# #     # don't forget to remove observer, or the
# #     # monitor will poll forever...
# #     cardmonitor.deleteObserver(cardobserver)

# #     import sys
# #     if 'win32' == sys.platform:
# #         print('press Enter to continue')
# #         sys.stdin.read(1)


# # from smartcard.scard import *
# # import smartcard.util

# # srTreeATR = \
# #     [0x3B, 0x77, 0x94, 0x00, 0x00, 0x82, 0x30, 0x00, 0x13, 0x6C, 0x9F, 0x22]
# # srTreeMask = \
# #     [0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF]


# # def printstate(state):
# #     reader, eventstate, atr = state
# #     print(reader + " " + smartcard.util.toHexString(atr, smartcard.util.HEX))
# #     if eventstate & SCARD_STATE_ATRMATCH:
# #         print('\tCard found')
# #     if eventstate & SCARD_STATE_UNAWARE:
# #         print('\tState unware')
# #     if eventstate & SCARD_STATE_IGNORE:
# #         print('\tIgnore reader')
# #     if eventstate & SCARD_STATE_UNAVAILABLE:
# #         print('\tReader unavailable')
# #     if eventstate & SCARD_STATE_EMPTY:
# #         print('\tReader empty')
# #     if eventstate & SCARD_STATE_PRESENT:
# #         print('\tCard present in reader')
# #         return True
# #     if eventstate & SCARD_STATE_EXCLUSIVE:
# #         print('\tCard allocated for exclusive use by another application')
# #     if eventstate & SCARD_STATE_INUSE:
# #         print('\tCard in used by another application but can be shared')
# #     if eventstate & SCARD_STATE_MUTE:
# #         print('\tCard is mute')
# #     if eventstate & SCARD_STATE_CHANGED:
# #         print('\tState changed')
# #     if eventstate & SCARD_STATE_UNKNOWN:
# #         print('\tState unknowned')


# # try:
# #     hresult, hcontext = SCardEstablishContext(SCARD_SCOPE_USER)
# #     if hresult != SCARD_S_SUCCESS:
# #         raise error(
# #             'Failed to establish context: ' +
# #             SCardGetErrorMessage(hresult))
# #     print('Context established!')

# #     try:
# #         hresult, readers = SCardListReaders(hcontext, [])
# #         if hresult != SCARD_S_SUCCESS:
# #             raise error(
# #                 'Failed to list readers: ' +
# #                 SCardGetErrorMessage(hresult))
# #         print('PCSC Readers:', readers)

# #         readerstates = []
# #         for i in range(len(readers)):
# #             readerstates += [(readers[i], SCARD_STATE_UNAWARE)]

# #         print('----- Current reader and card states are: -------')
# #         hresult, newstates = SCardGetStatusChange(hcontext, 0, readerstates)
# #         for i in newstates:
# #             printstate(i)

# #         print('----- Please insert or remove a card ------------')
# #         hresult, newstates = SCardGetStatusChange(
# #                                 hcontext,
# #                                 INFINITE,
# #                                 newstates)

# #         print('----- New reader and card states are: -----------')
# #         for i in newstates:
# #             printstate(i)

# #     finally:
# #         hresult = SCardReleaseContext(hcontext)
# #         if hresult != SCARD_S_SUCCESS:
# #             raise error(
# #                 'Failed to release context: ' +
# #                 SCardGetErrorMessage(hresult))
# #         print('Released context.')

# #     import sys
# #     if 'win32' == sys.platform:
# #         print('press Enter to continue')
# #         sys.stdin.read(1)

# # except error as e:
# #     print(e)


# # from smartcard.scard import *

# # try:
# #     hresult, hcontext = SCardEstablishContext(SCARD_SCOPE_USER)
# #     if hresult != SCARD_S_SUCCESS:
# #         raise error(
# #             'Failed to establish context: ' +
# #             SCardGetErrorMessage(hresult))
# #     print('Context established!')

# #     try:
# #         hresult, readers = SCardListReaders(hcontext, [])
# #         if hresult != SCARD_S_SUCCESS:
# #             raise error(
# #                 'Failed to list readers: ' +
# #                 SCardGetErrorMessage(hresult))
# #         print('PCSC Readers:', readers)

# #         if len(readers) < 1:
# #             raise error('No smart card readers')

# #         for zreader in readers:
# #             print('Trying to perform transaction on card in', zreader)

# #             try:
# #                 hresult, hcard, dwActiveProtocol = SCardConnect(
# #                     hcontext,
# #                     zreader,
# #                     SCARD_SHARE_SHARED,
# #                     SCARD_PROTOCOL_T0 | SCARD_PROTOCOL_T1)
# #                 if hresult != SCARD_S_SUCCESS:
# #                     raise error(
# #                         'unable to connect: ' +
# #                         SCardGetErrorMessage(hresult))
# #                 print('Connected with active protocol', dwActiveProtocol)

# #                 try:
# #                     hresult = SCardBeginTransaction(hcard)
# #                     if hresult != SCARD_S_SUCCESS:
# #                         raise error(
# #                             'failed to begin transaction: ' +
# #                             SCardGetErrorMessage(hresult))
# #                     print('Beginning transaction')

# #                     hresult, reader, state, protocol, atr = SCardStatus(hcard)
# #                     if hresult != SCARD_S_SUCCESS:
# #                         raise error(
# #                             'failed to get status: ' +
# #                             SCardGetErrorMessage(hresult))
# #                     print('ATR:', end=' ')
# #                     for i in range(len(atr)):
# #                         print("0x%.2X" % atr[i], end=' ')
# #                     print("")

# #                 finally:
# #                     hresult = SCardEndTransaction(hcard, SCARD_LEAVE_CARD)
# #                     if hresult != SCARD_S_SUCCESS:
# #                         raise error(
# #                             'failed to end transaction: ' +
# #                             SCardGetErrorMessage(hresult))
# #                     print('Transaction ended')

# #                     hresult = SCardDisconnect(hcard, SCARD_UNPOWER_CARD)
# #                     if hresult != SCARD_S_SUCCESS:
# #                         raise error(
# #                             'failed to disconnect: ' +
# #                             SCardGetErrorMessage(hresult))
# #                     print('Disconnected')
# #             except error as message:
# #                 print(error, message)

# #     finally:
# #         hresult = SCardReleaseContext(hcontext)
# #         if hresult != SCARD_S_SUCCESS:
# #             raise error(
# #                 'failed to release context: ' +
# #                 SCardGetErrorMessage(hresult))
# #         print('Released context.')

# # except error as e:
# #     print(e)

# # import sys
# # if 'win32' == sys.platform:
# #     print('press Enter to continue')
# #     sys.stdin.read(1)
# from serial.tools import list_ports

# def get_serial_port():
#     port_dict={}
#     ports = list(list_ports.comports())
    
#     # if not ports:
#         # return frappe.throw("Please check for the connectivity of ports")
#     for port in ports:
#         # print("Port check:---->",port.product)
#         # print("port description:---->",port.product)
#         if port.description == "USB-Serial Controller D":
#             port_dict.update({"w_gross_machine_port":port.device})
#         if port.description == "USB-Serial Controller":
#             port_dict.update({"bell_switch_port":port.device})
#     return port_dict

# @staticmethod
# def execute_terminal_command(command,password=None):
#     try:
#         if password:
#             command = f"echo '{password}' | sudo -S {command}"
#         subprocess.run(command,shell=True,check=True,executable="/bin/bash")
#         return True
#     except subprocess.CalledProcessError as e:
#         if "Module not currently loded" in str(e):
#             print(f"Module not currently loaded: {command}")
#         else:
#             print(f"Command execution failed: {command}")
#         return True

# port  = get_serial_port()
# button_port_number = port.get("bell_switch_port")
# password = 8055

# command_sequence = [
#     f"sudo chmod 777 {button_port_number}"
# ]

# for command in command_sequence:
#     if not execute_terminal_command(command,password):
#         print("false")

# button_port = serial.Serial()
# button_port.baudrate = 9600
# button_port.timeout = 1
# button_port.bytesize = serial.EIGHTBITS
# button_port.stopbits = serial.STOPBITS_ONE
# button_port.parity = serial.PARITY_NONE
# button_port.port = button_port_number

# try:
#     if button_port.is_open:
#         button_port.close()
#     button_port.open()
    
#     x=0
#     buff = ""
#     while True:
#         # play_audio(audio_profile="Press green button for weight")
#         button_port.write(b"D")
#         time.sleep(0.1)
#         # buff = button_port.read_all().decode('utf-8')
#         buff = button_port.read_all().decode('latin-1')
#         if x >=5000:
#             print("false")
#         if buff == "D":
#             print("button pressed ==============>")

# except Exception as e:
#     print("Error:--->",e)


# # def insert_document_with_child(doc):
# #     PROFILE = frappe.get_doc("Weighment Profile")
# #     URL = PROFILE.get("weighment_server_url")
# #     API_KEY = PROFILE.get("api_key")
# #     API_SECRET = PROFILE.get_password("api_secret")
# #     data = doc.as_dict()
# #     headers = {
# #         "Authorization": f"token {API_KEY}:{API_SECRET}",
# #         "Content-Type": "application/json"
# #     }
# #     try:
# #         items = []
# #         for item in doc.items:
# #             item_dict = item.as_dict()
# #             to_remove = ["name", "owner", "creation", "modified", "modified_by", "doctype", "parent", "parenttype", "parentfield"]
# #             for r in to_remove:
# #                 if item_dict.get(r):
# #                     item_dict.pop(r)
# #             items.append(item_dict)
        
# #         fields_to_check = ["driver", "transporter"]
# #         for field in fields_to_check:
# #             if data.get(field) and "~" in data.get(field):
# #                 field_value = data.pop(field)
# #                 actual_value = field_value.split("~")[0]
# #                 data[field] = actual_value
        
# #         data.update({
# #             "items":items
# #         })

# #         payload = json.dumps(data)

# #         response = requests.post(f"{URL}/api/resource/{doc.doctype}", data=payload, headers=headers)
# #         if response.status_code == 200:
# #             frappe.msgprint(
# #                 title="Recored Created",
# #                 indicator="orange",
# #                 alert=True,
# #                 realtime=True,
# #                 msg=" Record Created Sucessfully ... ")
# #         else:
# #             print("Error:", response.text)
# #     except Exception as e:
# #         frappe.error_log(f"Exception occurred: {e}")
# #         print("Exception:", e)


# import serial
# from serial.tools import list_ports
# # def get_serial_port():
# port_dict={}
# ports = list(list_ports.comports())

# for port in ports:
#     print("port device:---->",port.device)
#     print("port description:---->",port.description)
#     print("port device_path:---->",port.device_path)
#     print("port hwid:---->",port.hwid)
#     print("port location:---->",port.location)
#     print("port pid:---->",port.pid)
#     print("port serial_number:---->",port.serial_number)


# try:
#     from smartcard.utils import toHexString
#     print("smartcard.utils module is available")
# except ImportError as e:
#     print(f"Error: {e}")


# def func (x):
#     if x <= 1:
#         return 1
#     else:
#         return x * func(x-1)
    
# print(func(4))