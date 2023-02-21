import os
import re
import sys
import time
import threading
import pygame
import serial
import customtkinter
import tkinter
from PIL import Image

# ---------------------------------------------------------------------------------------------
# TK APP class inizialitation
class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()
# ---------------------------------------------------------------------------------------------

# ---------------------------------------------------------------------------------------------
        # Initialize pygame module (needed to display images in the DLP)
        pygame.init()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()

        # Set the display mode to the second monitor (Adjust in Windows [W + P], EXTEND MODE )
        global screen
        global screen_GUI
        screen = pygame.display.set_mode(
            (1024, 768), pygame.FULLSCREEN, display=1)
        # Needed to avoid conflicts between GUI CTk window and Pygame window
        screen_GUI = pygame.display.set_mode((1024, 768), display=0)

        # Get the list of images in the folder
        images_folder = 'images'
        images = [image for image in os.listdir(
            images_folder) if image.endswith('.jpg') or image.endswith('.png')]

        # Displays the image selected in the DLP
        def show_image(image_number):
            # Display the specified image
            image_name = images[image_number]
            image = pygame.image.load(os.path.join(images_folder, image_name))
            screen.blit(image, (0, 0))
            pygame.display.update()

        # Displays a black background in the DLP
        def show_black():
            # Fill the screen with black color
            screen.fill((0, 0, 0))
            pygame.display.update()

        show_black()  # Display black as soon as possible to avoid unwanted solidification
# ---------------------------------------------------------------------------------------------

# ---------------------------------------------------------------------------------------------
        # Check Motor state (moving/stopped) to synchronize DLP projection and avoid Buffer errors
        def checkMotor(ii):
            cc = 0

            if ii == 0:  # Motor HOME
                update_textbox("\nHoming...")
                while True:
                    # Se utiliza esta flag para evitar una primera lectura errónea (descarta las 4 primeras medidas)
                    cc = cc + 1
                    selected_pin1 = str(3)
                    ser2.write(str(selected_pin1).encode())
                    pin_value1 = ser2.readline().decode().strip()
                    if cc > 25:
                        if pin_value1 == str(1):  # Se pulsa el final de carrera
                            pin_value1 = 0
                            update_textbox("\nHoming Done!")
                            time.sleep(10)
                            break

            if ii == 1:  # Motor PRINTING
                while True:
                    selected_pin1 = str(3)
                    selected_pin2 = str(4)

                    ser2.write(str(selected_pin1).encode())
                    pin_value1 = ser2.readline().decode().strip()

                    ser2.write(str(selected_pin2).encode())
                    pin_value2 = ser2.readline().decode().strip()

                    # Está parado (Ha finalizado un comando gcode)
                    # El final de carrerea no está pulsado y el motor está parado
                    if pin_value2 == str(1) and pin_value1 == str(0):
                        break
# ---------------------------------------------------------------------------------------------

# ---------------------------------------------------------------------------------------------
# App design

        # App title and window size
        self.title("DLP 3D Bioprinter Controller | BTELab")
        self.geometry("820x610")

        # Set grid layout 1x2 (matrix type)
        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # Create Output Terminal textbox
        self.cmd_frame = customtkinter.CTkFrame(
            self, corner_radius=0, height=40, fg_color="transparent")
        self.cmd_frame.grid(row=2, column=0, columnspan=2,
                            sticky="nsew", pady=10)
        self.cmd_frame.rowconfigure(0, weight=1)
        self.cmd_frame.columnconfigure(0, weight=1)

        self.textbox = customtkinter.CTkTextbox(
            self.cmd_frame, activate_scrollbars=True, height=70, width=500, pady=3, padx=10, state="normal")
        self.textbox.pack()

        # Function to print text in terminal from anywhere in the code
        def update_textbox(text):
            self.textbox.insert(tkinter.END, text)
            # Auto scroll down to always see new messages
            self.textbox.see(tkinter.END)

        update_textbox("... 3D DLP Bioprinter ...")
# ---------------------------------------------------------------------------------------------

# ---------------------------------------------------------------------------------------------
# Set serial communication with Arduino Mega 2560 (Marlin) and Arduino Nano (Sensoring)
        global ser1
        global ser2
        
        ser1 = serial.Serial(str("COM7"), 115200)  # Arduino Mega Marlin
        ser2 = serial.Serial(str("COM9"), 112500)  # Arduino Nano Sensoring
        time.sleep(1)  # Must be here to avoid errors

        # Check if both serial connections are active
        if ser1.is_open and ser2.is_open:
            update_textbox("\nSerial connections are active and ready.")
        else:
            update_textbox("\nError: Serial connections failed.")
# ---------------------------------------------------------------------------------------------

# ---------------------------------------------------------------------------------------------
        # Create warning bottom frame and label (images must be loaded into 'images' folder)
        self.bottom_frame = customtkinter.CTkFrame(
            self, bg_color=("gray70", "gray30"), corner_radius=0, height=30)
        self.bottom_frame.grid(row=1, column=0, columnspan=2, sticky="nsew")
        self.bottom_frame.rowconfigure(0, weight=1)
        self.bottom_frame.columnconfigure(0, weight=1)

        self.bottom_frame_label = customtkinter.CTkLabel(self.bottom_frame, text="WARNING: Slicer images must be already imported into the 'images' folder ", font=customtkinter.CTkFont(
            size=12, weight="bold", slant="italic"), bg_color=("gray70", "gray30"), anchor="center")
        self.bottom_frame_label.grid(
            row=0, column=0, columnspan=2, sticky="nsew")
        self.bottom_frame_label.grid(pady=5, padx=5, sticky="nsew")

        # Load Logo and Menu Images with light and dark mode image
        image_path = os.path.join(os.path.dirname(
            os.path.realpath(__file__)), "GUI_images")
        self.logo_image = customtkinter.CTkImage(Image.open(
            os.path.join(image_path, "logo.jpeg")), size=(46, 46))
        self.print_image = customtkinter.CTkImage(light_image=Image.open(os.path.join(image_path, "print_dark.png")),
                                                  dark_image=Image.open(os.path.join(image_path, "print_light.png")), size=(30, 30))
        self.chat_image = customtkinter.CTkImage(light_image=Image.open(os.path.join(image_path, "calibration_dark.png")),
                                                 dark_image=Image.open(os.path.join(image_path, "calibration_light.png")), size=(25, 25))
        self.add_user_image = customtkinter.CTkImage(light_image=Image.open(os.path.join(image_path, "gcode_dark.png")),
                                                     dark_image=Image.open(os.path.join(image_path, "gcode_light.png")), size=(30, 30))

        # Create navigation frame
        self.navigation_frame = customtkinter.CTkFrame(self, corner_radius=0)
        self.navigation_frame.grid(row=0, column=0, sticky="nsew")
        self.navigation_frame.grid_rowconfigure(4, weight=1)

        self.navigation_frame_label = customtkinter.CTkLabel(self.navigation_frame, text="  DLP 3D Bioprinting", image=self.logo_image,
                                                             compound="left", font=customtkinter.CTkFont(size=15, weight="bold"))  # Title
        self.navigation_frame_label.grid(row=0, column=0, padx=20, pady=20)

        self.print_button = customtkinter.CTkButton(self.navigation_frame, corner_radius=0, height=40, border_spacing=10, text="Auto Print",
                                                    fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"),
                                                    image=self.print_image, anchor="w", command=self.print_button_event)  # Auto Print menu
        self.print_button.grid(row=1, column=0, sticky="ew")

        self.calibration_frame_button = customtkinter.CTkButton(self.navigation_frame, corner_radius=0, height=40, border_spacing=10, text="  Calibration",
                                                                fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"),
                                                                image=self.chat_image, anchor="w", command=self.calibration_frame_button_event)  # Calibration menu
        self.calibration_frame_button.grid(row=2, column=0, sticky="ew")

        self.gcode_frame_button = customtkinter.CTkButton(self.navigation_frame, corner_radius=0, height=40, border_spacing=10, text="Manual Mode",
                                                          fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"),
                                                          image=self.add_user_image, anchor="w", command=self.gcode_frame_button_event)  # Manual Mode
        self.gcode_frame_button.grid(row=3, column=0, sticky="ew")
# ---------------------------------------------------------------------------------------------

# ---------------------------------------------------------------------------------------------
        # Variable definitions to store COM port selection in variable
        selected_port_mega = customtkinter.StringVar(value="COM7")     
        selected_port_nano = customtkinter.StringVar(value="COM9")
        
        # Refresh connection function
        def refresh_con(self):
            global ser1
            global ser2
            
            ser1.close()
            ser2.close()
            
            print(selected_port_mega.get())

            ser1 = serial.Serial(selected_port_mega.get(), 115200)  # Arduino Mega Marlin
            ser2 = serial.Serial(selected_port_nano.get(), 112500)  # Arduino Nano Sensoring
            time.sleep(1)  # Must be here to avoid errors

            # Check if both serial connections are active
            if ser1.is_open and ser2.is_open:
                update_textbox("\nSerial connections are active and ready.")
            else:
                update_textbox("\nError: Serial connections failed.")

        # COM serial port selection for Arduino Mega
        self.navigation_frame_label2 = customtkinter.CTkLabel(
            self.navigation_frame, text="Arduino Mega w/ Marlin", font=customtkinter.CTkFont(size=13))  # Title
        self.navigation_frame_label2.grid(
            row=4, column=0, padx=20, pady=(5, 5))
        self.appearance_mode_menu2 = customtkinter.CTkOptionMenu(self.navigation_frame, width=100, button_color="purple", fg_color="purple", values=[
            "COM1", "COM2", "COM3", "COM4", "COM5", "COM6", "COM7", "COM8", "COM9", "COM10", "COM11", "COM12", "COM13", "COM14"], variable=selected_port_mega,  command=refresh_con)  # ARDUINO Mega PORT
        self.appearance_mode_menu2.grid(
            row=4, column=0, padx=20, pady=(0, 5), sticky="s")

        # COM serial port selection for Arduino Nano
        self.navigation_frame_label1 = customtkinter.CTkLabel(
            self.navigation_frame, text="Arduino Nano", font=customtkinter.CTkFont(size=13))  # Title
        self.navigation_frame_label1.grid(
            row=5, column=0, padx=20, pady=(0, 50))
        appearance_mode_menu1 = customtkinter.CTkOptionMenu(self.navigation_frame, width=100, button_color="purple", fg_color="purple", variable=selected_port_nano, values=[
            "COM1", "COM2", "COM3", "COM4", "COM5", "COM6", "COM7", "COM8", "COM9", "COM10", "COM11", "COM12", "COM13", "COM14"], command=refresh_con)  # ARDUINO MEGA + MARLIN PORT

        appearance_mode_menu1.grid(
            row=5, column=0, padx=20, pady=(30, 30), sticky="s")
# ---------------------------------------------------------------------------------------------

# ---------------------------------------------------------------------------------------------
        # Select screen light mode
        self.appearance_mode_menu = customtkinter.CTkOptionMenu(self.navigation_frame, values=["Dark", "Light", "System"],
                                                                command=self.change_appearance_mode_event)  # Window light style menu
        self.appearance_mode_menu.grid(
            row=6, column=0, padx=20, pady=20, sticky="s")
# ---------------------------------------------------------------------------------------------

# ---------------------------------------------------------------------------------------------
# 1. Create Print Menu frame

        def apply():  # Function to get new values of Process Parameters using an "apply" button

            # Variables that are only referenced inside functions --> Implicitly global
            global exposure_time
            global lift_distance
            global layer_height
            global bed_temp

            # CTk StringVar to float
            layer_height = float(layer_height_var.get())
            # CTk StringVar to float
            exposure_time = float(exposure_time_var.get())
            # CTk StringVar to float
            lift_distance = float(lift_distance_var.get())
            # CTk StringVar to float
            bed_temp = float(bed_temp_var.get())

            update_textbox("\nParameters Updated!")
# ---------------------------------------------------------------------------------------------

# ---------------------------------------------------------------------------------------------
        # Function that ensures calibration
        def startprint():
            response = tkinter.messagebox.askquestion(
                "Calibration Required", "Has the printer been calibrated?")

            # Call the appropriate function based on the user's response
            if response == 'yes':
                apply()
                update_textbox("\nPrinting...")
                # Threading is used so that window can still be used in the main thread.
                threading.Thread(target=printing).start()
            else:
                update_textbox("\nCalibrate First Please!")
# ---------------------------------------------------------------------------------------------

# ---------------------------------------------------------------------------------------------
        # Function to stop print
        def quit():  # Called by STOP button in GUI. Exits the printing function.
            global ser1
            global ser2
            ser1.close()  # Stops print
            ser2.close()  # Stops print
            time.sleep(1)
            show_black()
            ser1 = serial.Serial('COM7', 115200)  # Arduino Mega Marlin
            ser2 = serial.Serial('COM9', 112500)  # Arduino Nano Sensoring
            time.sleep(1)  # Must be here to avoid errors
# ---------------------------------------------------------------------------------------------

# ---------------------------------------------------------------------------------------------
        # Structure frame of Print Menu
        self.print_frame = customtkinter.CTkFrame(
            self, corner_radius=0, fg_color="transparent")
        self.print_frame.grid_columnconfigure(0, weight=1)

        # Window Title
        parameters_label = customtkinter.CTkLabel(
            master=self.print_frame, text="Process Parameters", font=("Roboto", 14, "bold"))
        parameters_label.pack(pady=10, padx=20)

        # Entry for Layer Height
        layer_height_UI = customtkinter.CTkLabel(
            master=self.print_frame, text="Layer Height (mm)")
        layer_height_UI.pack()

        layer_height_var = tkinter.StringVar(value="0.05")
        layer_heights = customtkinter.CTkEntry(
            master=self.print_frame, width=50, height=10, textvariable=layer_height_var)
        layer_heights.pack(pady=(0, 5))

        # Entry for Exposure Time
        exposure_time_UI = customtkinter.CTkLabel(
            master=self.print_frame, text="Exposure Time (s)")
        exposure_time_UI.pack()

        exposure_time_var = customtkinter.StringVar(value="5")
        exposure_times = customtkinter.CTkEntry(
            master=self.print_frame, width=50, height=10, textvariable=exposure_time_var)
        exposure_times.pack(pady=(0, 5))

        # Entry for Lift Distance
        lift_distance_UI = customtkinter.CTkLabel(
            master=self.print_frame, text="Lift Distance (mm)")
        lift_distance_UI.pack()

        lift_distance_var = tkinter.StringVar(value="5")
        lift_distances = customtkinter.CTkEntry(
            master=self.print_frame, width=50, height=10, textvariable=lift_distance_var)
        lift_distances.pack(pady=(0, 5))

        # Entry for Bed Temperature
        bed_temp_UI = customtkinter.CTkLabel(
            master=self.print_frame, text="Bed Temperature (ºC)")
        bed_temp_UI.pack()

        bed_temp_var = tkinter.StringVar(value="27")
        bed_temps = customtkinter.CTkEntry(
            master=self.print_frame, width=50, height=10, textvariable=bed_temp_var)
        bed_temps.pack(pady=(0, 5))

        # Apply button
        applys = customtkinter.CTkButton(
            master=self.print_frame, text="Set Values", command=apply, width=50, fg_color="gray")
        applys.pack(pady=10, padx=10)

        # Start Printing button
        start_printing = customtkinter.CTkButton(
            master=self.print_frame, text="START PRINT", command=startprint, width=150, height=50, fg_color="green")
        start_printing.pack(pady=(30, 10), padx=10)

        # Stop Printing button
        stop_printing = customtkinter.CTkButton(
            master=self.print_frame, text="STOP PRINT", command=quit,  width=100, height=50, fg_color="red")
        stop_printing.pack(pady=(0, 30), padx=10)
# ---------------------------------------------------------------------------------------------

# ---------------------------------------------------------------------------------------------
        # Printing loop (Gcode serial sending + DLP images projection)
        def printing():
            global exposure_time
            global lift_distance
            global layer_height
            global bed_temp

            # Starting and setting commands
            show_black()
            ser1.write(('G21\n').encode())  # Set units to be mm
            ser1.write(('G90\n').encode())  # Absolute Positioning

            # Bed temperature (hot bed + thermistor needed)
            # Set bed temperature
            # ser1.write(('M140 S{}\n'.format(bed_temp)).encode())
            # Wait for bed temperature to reach
            # ser1.write(('M190 S{}\n'.format(bed_temp)).encode())

            z_ii = 0  # Flag para las alturas de capa
            jj = 0  # Flag para el número de imagen a proyectar

            # Layer number n
            for filename in os.listdir(images_folder):

                # Target layer Z movement
                ser1.write(('G1 Z{}\n'.format(z_ii)).encode())
                threading.Thread(target=checkMotor(1)).start()

                # Display image in DLP
                update_textbox(f"\nLayer: {jj + 1}")
                show_image(jj)
                time.sleep(exposure_time)

                # Turn black DLP before changing position2
                show_black()
                time.sleep(0.5)

                # Perform lift distance before new layer height
                ser1.write(('G1 Z{}\n'.format(z_ii + lift_distance)).encode())
                threading.Thread(target=checkMotor(1)).start()

                # Update flags
                z_ii += layer_height
                jj += 1

            # For the last layer lift extra distance
            ser1.write(('G1 Z{}\n'.format(z_ii + 3*lift_distance)).encode())
            threading.Thread(target=checkMotor(1)).start()
# ---------------------------------------------------------------------------------------------

# ---------------------------------------------------------------------------------------------
# 2. Create Print Menu frame

        """
        Cuando se realiza un homing, marlin automáticamente hace que en la posición del final de carrera Z=Z_MAX_POS=60, anulando las posiciones dadas por el Z=0 previo (si se calibra únicamente haciendo un g92 Z0).

        El alogoritmo de calibración propuesto es el siguiente:
        1. Con la máquina apagada, mover el motor y  llevar la cama de impresión hacia el fondo del tanque de la resina y colocar a una altura de capa aproximadamente.
        2. Pulsar el botón de calibrado "SET NEW ZERO". Esto hará lo siguiente:
            i. En la altura en la que se ha posicionado la plataforma (primera capa Z0), se realiza un M114 para leer las coordenadas del eje Z.
            ii. Se mueve el motor lo suficiente para que se active el final de carrera (evitando hacer un G28).
            iii. Se realiza otro M114 para leer la coordenada Z en la posición más alta.
            iv. La diferencia de las dos medidas es la distancia desde la posición del final de carrera a la primera capa y se utiliza para establecer el cero.
        """

        # Function created to allow threading when calling calibration function, so that main window doesnt freeze
        def setzerocall():
            threading.Thread(target=calsetzero).start()

        # Set to Zero calibration function:
        def calsetzero():

            update_textbox("\nCalibrating...")

            # Send M114 command to get current position (Z0)
            ser1.write(('M114\n').encode())

            # Define the regular expression pattern to match the second z value
            # X:0.00Y:0.00Z:0.00E:0.00 Count X: 0.00Y:0.00Z:0.00
            pattern = r'Z:(-?\d+\.\d+)'

            # Loop to read the M114 output
            while True:
                response0 = ser1.readline().decode('utf-8').strip()
                if response0.startswith('X:'):
                    # Extract Z from response
                    matches = re.findall(pattern, response0)
                    z_position0 = float(matches[1])
                    break  # Stop reading after getting the first valid response

            update_textbox(f"\nZ0 coordinate: {z_position0}")

            # Raise print platform until the limit switch is hit.
            ser1.write(('G1 Z100\n').encode())
            threading.Thread(target=checkMotor(0)).start()

            # Send M114 command to get current position (Zmax)
            ser1.write(('M114\n').encode())

            # Loop to read the M114 output
            while True:
                response1 = ser1.readline().decode('utf-8').strip()
                if response1.startswith('X:'):
                    # Extract Z from response
                    matches = re.findall(pattern, response1)
                    z_position1 = float(matches[1])
                    break  # Stop reading after getting the first valid response

            update_textbox(f"\nZmax coordinate: {z_position1}")

            zmax = z_position1 - z_position0

            update_textbox(f"\nZ range: {zmax}")

            # Send G28, so that printer can move any direction from here.
            ser1.write(('G28').encode())

            # Calibration
            ser1.write(('G92 Z{}\n'.format(zmax)).encode())

            # Send M114 command to get current position
            ser1.write(('G90\n G1 Z0\n').encode())
            threading.Thread(target=checkMotor(1)).start()

            ser1.write(('G1 Z25\n').encode())
            threading.Thread(target=checkMotor(1)).start()

        # Structure frame
        self.calibration_frame = customtkinter.CTkFrame(
            self, corner_radius=0, fg_color="transparent")

        # Insert Calibration title
        calibration_label = customtkinter.CTkLabel(
            master=self.calibration_frame, text="Calibration", font=("Roboto", 16, "bold"))
        calibration_label.pack(pady=(10, 0))

        calibrationsub_label = customtkinter.CTkLabel(
            master=self.calibration_frame, text="Follow the instructions below: ", font=("Roboto", 11))
        calibrationsub_label.pack(pady=(0, 23.5))

        # Calibration instructions
        instruc1_label = customtkinter.CTkLabel(
            master=self.calibration_frame, text="Always calibrate after homing (G28)\n\n\n\n 1. Remove the power from the motor and move the stage manually to the desired \n first layer Z0 (one layer height above the bottom plate.)", font=("Roboto", 14))
        instruc1_label.pack(pady=(10, 10))

        instruc2_label = customtkinter.CTkLabel(
            master=self.calibration_frame, text="2. Restart this app so that serial connection can be re-established.", font=("Roboto", 14))
        instruc2_label.pack(pady=(10, 10))

        instruc3_label = customtkinter.CTkLabel(
            master=self.calibration_frame, text="3. Click on the following button to set the current position to the new 'Zero' Z0:", font=("Roboto", 14))
        instruc3_label.pack(pady=(10, 40))

        # Set coordinates (new zero) button. Threading is used so that window can still be used in the main thread.
        new_zero = customtkinter.CTkButton(
            master=self.calibration_frame, text="SET NEW ZERO", command=setzerocall, width=100, height=40, fg_color="green")
        new_zero.pack(pady=(10, 100), padx=10)
# ---------------------------------------------------------------------------------------------

# ---------------------------------------------------------------------------------------------
# 3. Create Manual and Gcode Menu frame

        def gcodeinterp(): # Function to read and send gcode commands
            try:
                # Gets inserted gcode
                gcode = str(gcode_var.get())
                # Run gcode
                ser1.write(('G90\n {}\n'.format(gcode)).encode())
            except:
                update_textbox("\nInvalid Gcode!")
            update_textbox(f"\n{gcode} Sent!")

        def manualhome(): # Function to home after pressing button
            # Run gcode
            ser1.write(('G28 \n').encode())
            update_textbox("\nHoming...")

        def gotozero(): # Function to go Z0 after pressing button
            # Run gcode
            ser1.write(('G90\n G1 Z0 \n').encode())
            update_textbox("\nGoing to Z0...")

        # Functions to move with relative coordinates manually
        def rel_positioning1():
            # Run gcode
            ser1.write(('G91\n G1 Z1\n').encode())  # Relative positioning
            update_textbox("\nMoving up 1 mm")

        def rel_positioning10():
            # Run gcode
            ser1.write(('G91\n G1 Z10\n').encode())  # Relative positioning
            update_textbox("\nMoving up 10 mm")

        def rel_positioningd1():
            # Run gcode
            ser1.write(('G91\n G1 Z-1\n').encode())  # Relative positioning
            update_textbox("\nMoving down 1 mm")

        def rel_positioningd10():
            # Run gcode
            ser1.write(('G91\n G1 Z-10\n').encode())  # Relative positioning
            update_textbox("\nMoving down 10 mm")

        def shwimg(): # Show selected img
            # Gets inserted gcode
            imgin = int(noimg_var.get())
            show_image(imgin)
            update_textbox(f"\nShowing img n: {imgin}")

        def shwblack(): # Show black background
            # Gets inserted gcode
            show_black()
            update_textbox("\nBlack background.")

        # Structure frame
        self.gcode_frame = customtkinter.CTkFrame(
            self, corner_radius=0, fg_color="transparent")
        self.gcode_frame.grid_columnconfigure(0, weight=1)

        # Insert Gcode title
        gcode_label = customtkinter.CTkLabel(
            master=self.gcode_frame, text="Insert Gcode:", font=("Roboto", 16, "bold"))
        gcode_label.pack(pady=(10, 5))

        # Gcode entry with Home Z by default
        gcode_var = tkinter.StringVar(value="G28 Z")
        gcode = customtkinter.CTkEntry(
            master=self.gcode_frame, width=250, height=25, textvariable=gcode_var)
        gcode.pack()

        # Send Gcode button
        send_gcode = customtkinter.CTkButton(
            master=self.gcode_frame, text="SEND", command=gcodeinterp, width=100, height=25, fg_color="green")
        send_gcode.pack(pady=(5, 0), padx=10)

        # Manual Control Title
        mcontrol_label = customtkinter.CTkLabel(
            master=self.gcode_frame, text="Manual Control (Always run first GO HOME):", font=("Roboto", 14, "bold"))
        mcontrol_label.pack(pady=(15, 2))

        # Go Home Button
        gohome_gcode = customtkinter.CTkButton(
            master=self.gcode_frame, corner_radius=10, width=80, height=25, text="GO HOME", command=manualhome, fg_color="red")
        gohome_gcode.pack(pady=(2, 17))

        # Go Go up 10 mm Button
        up10 = customtkinter.CTkButton(
            master=self.gcode_frame, corner_radius=10, width=160, height=25, text="Up 10 mm", command=rel_positioning10, fg_color="gray")
        up10.pack(pady=(0, 0))

        # Go up 1 mm Button
        up1 = customtkinter.CTkButton(
            master=self.gcode_frame, corner_radius=10, width=80, height=25, text="Up 1 mm", command=rel_positioning1, fg_color="gray")
        up1.pack(pady=2)

        # Go Zero Button
        gozero_gcode = customtkinter.CTkButton(
            master=self.gcode_frame, corner_radius=10, width=80, height=25, text="GO ZERO", command=gotozero, fg_color="blue")
        gozero_gcode.pack(pady=2)

        # Go Go down 1 mm Button
        down1 = customtkinter.CTkButton(
            master=self.gcode_frame, corner_radius=10, width=80, height=25, text="Down 1 mm", command=rel_positioningd1, fg_color="gray")
        down1.pack(pady=2)

        # Go down 10 mm Button
        down10 = customtkinter.CTkButton(
            master=self.gcode_frame, corner_radius=10, width=160, height=25, text="Down 10 mm", command=rel_positioningd10, fg_color="gray")
        down10.pack(pady=(2, 21))

        # DLP projection Title
        dlpproj_label = customtkinter.CTkLabel(
            master=self.gcode_frame, text="DLP projection", font=("Roboto", 14, "bold"))
        dlpproj_label.pack(pady=(0, 2))

        # Number of image entry
        noimg_var = tkinter.IntVar(value=120)
        noimg = customtkinter.CTkEntry(
            master=self.gcode_frame, width=50, height=25, textvariable=noimg_var)
        noimg.pack()

        # Display image button
        send_img = customtkinter.CTkButton(
            master=self.gcode_frame, text="DISPLAY IMAGE", width=160, command=shwimg, height=25, fg_color="green")
        send_img.pack(pady=(5, 0), padx=10)

        # Display black
        send_black = customtkinter.CTkButton(
            master=self.gcode_frame, text="BLACK PROJECTION", command=show_black, width=160, height=25, fg_color="purple")
        send_black.pack(pady=(5, 20), padx=10)
# ---------------------------------------------------------------------------------------------

# ---------------------------------------------------------------------------------------------
        # Select default frame
        self.select_frame_by_name("print")
# ---------------------------------------------------------------------------------------------

# ---------------------------------------------------------------------------------------------
# Left Menu to select between "1. Autoprint", "2. Calibration", "3. Manual/Gcode"
    def select_frame_by_name(self, name):
        # set button color for selected button
        self.print_button.configure(
            fg_color=("gray75", "gray25") if name == "print" else "transparent")
        self.calibration_frame_button.configure(fg_color=(
            "gray75", "gray25") if name == "calibration_frame" else "transparent")
        self.gcode_frame_button.configure(
            fg_color=("gray75", "gray25") if name == "gcode_frame" else "transparent")

        # Show selected frame
        if name == "print":
            self.print_frame.grid(row=0, column=1, sticky="nsew")
        else:
            self.print_frame.grid_forget()
        if name == "calibration_frame":
            self.calibration_frame.grid(row=0, column=1, sticky="nsew")
        else:
            self.calibration_frame.grid_forget()
        if name == "gcode_frame":
            self.gcode_frame.grid(row=0, column=1, sticky="nsew")
        else:
            self.gcode_frame.grid_forget()

    def print_button_event(self):
        self.select_frame_by_name("print")

    def calibration_frame_button_event(self):
        self.select_frame_by_name("calibration_frame")

    def gcode_frame_button_event(self):
        self.select_frame_by_name("gcode_frame")

    def change_appearance_mode_event(self, new_appearance_mode):
        customtkinter.set_appearance_mode(new_appearance_mode)
# ---------------------------------------------------------------------------------------------

# ---------------------------------------------------------------------------------------------
# Main loop and closing functions. Threrading is needed to avoid window lags.
def on_closing():
    ser1.close()
    ser2.close()
    if tkinter.messagebox.askokcancel("Quit", "Do you want to quit?"):
        os._exit(0)

def on_closing_threaded():
    threading.Thread(target=on_closing).start()

if __name__ == "__main__":
    app = App()
    app.protocol("WM_DELETE_WINDOW", on_closing_threaded) # Message to ensure window closing
    threading.Thread(target=app.mainloop()).start()
# ---------------------------------------------------------------------------------------------