########################################################
# CIS 422
# Project 1
# Group Members: Quinn Milionis, Parsa Bagheri,
#                 Ashton Shears, Samuel Champer, Marc Lee
########################################################

import os  # For file paths and for os specific line endings.
import calbackend  # Most backend functions for the calendar.
import caltime  # Time functions for the calendar.
import arrow  # For manipulating time objects.
from tkinter import *  # GUI library.
from tkinter import filedialog, messagebox  # Special imports from the GUI library.

# Global variables
days = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
months = ["January", "February", "March", "April", "May", "June",
          "July", "August", "September", "October", "November", "December"]
monthCounter = 0  # Incremented/decremented when forward/back buttons are pressed, it's the month that the user is on
yearCounter = 0  # Incremented/decremented according to change in month, it's the year that the user is on
dayCounter = 0 # Incremented/decremented according to change in day, it's the day that the user is on
selected_button_month = 0 # Holds the month that the selected day is on
selected_button_year = 0 # Holds the year that the selected day is on
selected_button = None # Holds the selected button
todayOrSelectedDay = "Today" # Will be used in the events frame

############################################################
# following class will be initialized upon running the app #
############################################################
class Calendar:
    def try_login(self, username, password):
        """
        Called when a user submits a username and password on the login screen.
        Prompts user if their authentication fails, 
        otherwise on success loads data from file into calendar and displays calendar
        args: string username
              string password
        """
        global menubar # Make a variable menubar and make it global, Menu bar holds the buttons in the top bar menu
        if not os.path.isfile(username + '.cal'):#IF CALENDAR FILE NOT FOUND FOR GIVEN USERNAME
            self.LOGIN_ERROR_LABEL.configure(text='Invalid Username')
            return
        self.event_map = calbackend.EventMap(username, password) # Try to access backend fucntion EventMap, 
                                                                 # with given username and password
        if self.event_map.error == 1:##IF DECRYPTION WITH GIVEN PASSWORD FAILED
            self.LOGIN_ERROR_LABEL.configure(text='Invalid Password')
        else:##SUCCESS
            self.login_frame.pack_forget()
            menubar.entryconfig("File", state="normal") # If login is successful, make the items in menu bar clickable
            self.create_main_menu(self.current_day, self.current_month, self.current_year, #Create the main menu, 
                                  self.first_day_of_month, self.num_days_in_month)         #which shows calendar and events

    def create_user(self, username, password):
        """
        Called on the login screen when a user selects the create user button
        args: string username
              string password
        """
        if os.path.isfile(username + '.cal'):#IF A CALENDAR FILE FOR GIVEN USERNAME ALREADY EXISTS
            self.LOGIN_ERROR_LABEL.configure(text='Username is taken')
        elif len(username) > 32 or len(password) > 32:
            self.LOGIN_ERROR_LABEL.configure(text="Max length username and password is 32")
        elif len(username) < 1:
            self.LOGIN_ERROR_LABEL.configure(text="Must include a Username")
        elif len(password) < 1:
            self.LOGIN_ERROR_LABEL.configure(text="Must include a Password")
        else:#CREATE A USER WITH GIVEN CREDENTIALS AND LOGIN
            calbackend.new_user(username, password)
            self.try_login(username, password)

    def event_frame_done_button(self, oldevent=None):
        """
        A function to be called by the add events button "done" which
        saves changes, destroys the add event frame,
        and pushes calender back to the main menu
        """
        # If a previously defined event was being edited, remove it from the event map.
        if oldevent:
            self.event_map.pop(oldevent)

        global yearCounter, monthCounter, dayCounter

        # Following creates a start date time format for the new event
        start_datetime = self.dropdown_list[7].get() + " " + \
            self.dropdown_list[8].get() + ", " + \
            self.dropdown_list[6].get() + ", " + \
            self.dropdown_list[0].get() + ":" + \
            self.dropdown_list[1].get() + " " + \
            self.dropdown_list[2].get() # Start date time will get the start date and time and put it in this format:
                                        # MONTH DAY, YEAR, hr:min AM/PM

        # Following creates a end date time format for the new event
        end_datetime = self.dropdown_list[7].get() + " " + \
                       self.dropdown_list[8].get() + ", " + \
                       self.dropdown_list[6].get() + ", " + \
                       self.dropdown_list[3].get() + ":" + \
                       self.dropdown_list[4].get() + " " + \
                       self.dropdown_list[5].get() # End date time will get the start date and time and put it in this format:
                                                   # MONTH DAY, YEAR, hr:min AM/PM

        # Following will call the backend function, CalEvent to create a new event                                           
        new_event = calbackend.CalEvent(self.entry_list[0].get(), # Title
                                        start_datetime, end_datetime, # Start time and end time
                                        self.entry_list[1].get(), # Location
                                        self.entry_list[2].get(), # Description
                                        self.entry_list[3].get()) # Notes

        if new_event.start > new_event.end: # Check to see if start time and end time won't conflict
            result = messagebox.showerror("Bad event times",
                                          "Finish time must be equal to or after start time", icon='warning')
            return
        self.event_map.add(new_event) # If start time and end time won't conflict add them to the events
        yearCounter = new_event.start.year # Update the year that user is on
        monthCounter = new_event.start.month # Update the month that user is on
        dayCounter = new_event.start.day # Update the day that user is on

        self.event_window_close()

    def delete_event_button(self, event):
        """
        Called when selecting the delete button while viewing on event in the calendar.
        Deletes event from the event map and then returns to the calendar view.
        """
        self.event_map.pop(event) # Call the backend function pop, to remove the event from the map
        self.event_window_close() # Clean up, destroy all the widgets in add/edit/delete events

    def event_window_close(self):
        """
        Close the event window.
        """
        # Clean everything off the event frame:
        # Check if the widgets exist if they do, destroy them
        if self.entry_list:
            for i in self.entry_list: i.destroy()
        if self.label_list:
            for i in self.label_list: i.destroy()
        if self.windowlabel: self.windowlabel.destroy()
        if self.done_button: self.done_button.destroy()
        if self.delete_button: self.delete_button.destroy()
        if self.cancel_button: self.cancel_button.destroy()
        if self.dropDownMenu_d: self.dropDownMenu_d.destroy()
        if self.dropDownMenu_y: self.dropDownMenu_y.destroy()
        if self.dropDownMenu_m: self.dropDownMenu_m.destroy()
        if self.dropDownMenu_start_h: self.dropDownMenu_start_h.destroy()
        if self.dropDownMenu_start_min: self.dropDownMenu_start_min.destroy()
        if self.dropDownMenu_start_ampm: self.dropDownMenu_start_ampm.destroy()
        if self.dropDownMenu_fin_h: self.dropDownMenu_fin_h.destroy()
        if self.dropDownMenu_fin_min: self.dropDownMenu_fin_min.destroy()
        if self.dropDownMenu_fin_ampm: self.dropDownMenu_fin_ampm.destroy()

        if self.add_event_frame: self.add_event_frame.destroy()
        if self.mask_buttons_subframe: self.mask_buttons_subframe.destroy()

        self.destroy_calendar_frame() # Destroy the calender frame
        self.destroy_events_frame() # Destroy the events frame

        first_day, num_days = caltime.days(monthCounter, yearCounter) # Variables first day and num days,
                                                                      # are local to this function
                                                                      # They take the value of the first day and number of days
                                                                      # of the month that calendar is on

        self.create_calendar_frame(monthCounter, first_day, num_days) # Create calendar of the month we're on

        # Check if there is a button selected, if so the label of events frame will read the date of the selected day
        # Otherwise it will read todays date
        if selected_button == None:
            self.create_events_frame(self.event_map.events_in_day(self.current_year, self.current_month, dayCounter),
                                    dayCounter, self.current_month, self.current_year)
        else:
            self.create_events_frame(self.event_map.events_in_day(selected_button_year, selected_button_month, dayCounter),
                                    dayCounter, selected_button_month, selected_button_year)
        
        # Set the following to false, because the add/edit/delete events widgets were destroyed earlier in the function 
        self.add_event_frame_exists = False

    def add_event_helper(self):
        """
        a helper function for add_events, 
        It will dynamically update the number of days for a selected month and year
        """
        global months

        # "months.index(str(self.tkvar_m.get())) + 1" is the month specified in the dates drop down month menu
        # "int(self.tkvar_y.get())" is the year specified in the dates year drop down menu
      	# caltime.days returns a tuple "(first_day, num_days)", we're only interested in num_days, hence [1]
      	# nd is a class variable, it will keep being updated as long as the app is running
        self.nd = caltime.days(months.index(str(self.tkvar_m.get())) + 1, int(self.tkvar_y.get()))[1]
        self.d = [i for i in range(1, self.nd + 1)] # self.d is a list from 1 to the number of days, nd
        											# It's a class variable and will update based on 
        											# the selected month and year
        
        self.tkvar_d = StringVar(self.add_event_frame) # Update the day Option menu
        self.tkvar_d.set("1") # Set the default day to 1

        self.dropDownMenu_d = OptionMenu(self.add_event_frame, self.tkvar_d, *self.d) # Update the dropdown menu
        																			  # to take the values is the
        																			  # updated Option menu
        self.dropDownMenu_d.config(background="ivory2", width=5)
        self.dropDownMenu_d.place(x=400, y=60)

    def toggle_event_frame(self, event=None):
        """
        Destroys calendar frame, and creates a new frame on the left side of the screen (place of the calendar).
        Input Areas are created for the user to submit event info to be tracked by the destroy_calendar_frame.
        args:	backend object CalEvent event or None
        """
        # Check to see if the add_event_frame already exist, if so, destroy it
        if self.add_event_frame_exists == True:
            self.event_window_close()

        # Initializing local variables to default StringVar objects
        title = StringVar() # This will take the title string
        location = StringVar() # This will take the location string
        description = StringVar() # This will take the description string
        notes = StringVar() # This will take the notes string

        # if an event is passed to the function, the above variables will be set
        if event:
            title.set(event.title)
            location.set(event.location)
            description.set(event.description)
            notes.set(event.notes)
        global months, monthCounter, yearCounter, dayCounter
        self.destroy_calendar_frame()
        self.mask_event_buttons()

        years = [i for i in range(self.current_year, self.current_year + 20)] # Local variable is a list of years
        																	  # From current year to 20 years from now
        hrs = [12, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]						  # Local variable, list of hours in half a day
        mins = ["00", "15", "30", "45"]										  # Local variable, List of minutes user can choose from
        ampm = ["am", "pm"]													  # Local variable, List containing AM and PM

        self.add_event_frame = Frame(self.calendar_frame, width=604, height=620, bg="ivory2")
        self.add_event_frame.place(x=0, y=0)

        # This is the format of the entry list: date, title, location, description and notes
        self.entry_list = [Entry(), Entry(), Entry(), Entry()]

        # This is the format of the dropdown list:
        # start_hr, start_min, start_ampm, end_hr, end_min, end_ampm, year, month, day
        self.dropdown_list = [StringVar() for i in range(9)]
        self.label_list = [Label() for i in range (7)]
        # Labels: title, start, end, location, description, notes
        # These will be shown on left side of the frame
        label_strs = ["Date", "Start time:", "End time:", "Title:", "Location:", "Description:", "Notes:"]

        # Add a label to describe the window (edit event or add new event)
        if event:
            self.windowlabel = Label(self.add_event_frame, text="Edit Event:", bg="ivory2", font=("Courier", 20))
            self.windowlabel.place(x=210, y=10)
        else:
            self.windowlabel = Label(self.add_event_frame, text="Add Event:", bg="ivory2", font=("Courier", 20))
            self.windowlabel.place(x=215, y=10)

        for i in range(7):
            self.label_list[i] = Label(self.add_event_frame, text=label_strs[i], bg="ivory2")
            self.label_list[i].place(x=30, y=60 + (i * 60))

        # date drop down menu
        self.tkvar_y = StringVar(self.add_event_frame)
        if selected_button == None:
            self.tkvar_y.set(self.current_year)
        else:
            self.tkvar_y.set(selected_button_year)

        self.tkvar_m = StringVar(self.add_event_frame)
        if selected_button == None:
            self.tkvar_m.set(months[self.current_month-1])
        else:
            self.tkvar_m.set(months[selected_button_month-1])

        self.nd = caltime.days(self.current_month, self.current_year)[1]

        self.d = [i for i in range(1, self.nd + 1)]
        self.tkvar_d = StringVar(self.add_event_frame)
        self.tkvar_d.set(dayCounter)

        # Menu for choosing the day.
        self.dropDownMenu_d = OptionMenu(self.add_event_frame, self.tkvar_d, *self.d)
        self.dropDownMenu_d.config(background="ivory2", width=5)
        self.dropDownMenu_d.place(x=400, y=60)

        # Menu for choosing the year.
        self.dropDownMenu_y = OptionMenu(self.add_event_frame, self.tkvar_y, *years,
                                    command=lambda x: self.add_event_helper())
        self.dropDownMenu_y.config(background="ivory2", width=6)
        self.dropDownMenu_y.place(x=150, y=60)

        # Menu for choosing the month.
        self.dropDownMenu_m = OptionMenu(self.add_event_frame, self.tkvar_m, *months,
                                    command=lambda x: self.add_event_helper())
        self.dropDownMenu_m.config(background="ivory2", width=12)
        self.dropDownMenu_m.place(x=250, y=60)
        # end date

        self.dropdown_list[6] = self.tkvar_y
        self.dropdown_list[7] = self.tkvar_m
        self.dropdown_list[8] = self.tkvar_d

        # start times
        self.dropdown_list[0] = StringVar(self.add_event_frame)
        self.dropdown_list[0].set(hrs[0])
        if event: self.dropdown_list[0].set(event.start.hour % 12)

        self.dropdown_list[1] = StringVar(self.add_event_frame)
        self.dropdown_list[1].set(mins[0])
        if event:
            if event.start.minute != 0:
                self.dropdown_list[1].set(event.start.minute)

        self.dropdown_list[2] = StringVar(self.add_event_frame)
        self.dropdown_list[2].set(ampm[0])
        if event:
            if event.start.hour > 12: self.dropdown_list[2].set(ampm[1])

        # Drop down for start hour.
        self.dropDownMenu_start_h = OptionMenu(self.add_event_frame, self.dropdown_list[0], *hrs)
        self.dropDownMenu_start_h.config(background="ivory2", width=5)
        self.dropDownMenu_start_h.place(x=150, y=120)

        # Drop down for start minute.
        self.dropDownMenu_start_min= OptionMenu(self.add_event_frame, self.dropdown_list[1], *mins)
        self.dropDownMenu_start_min.config(background="ivory2", width=5)
        self.dropDownMenu_start_min.place(x=210, y=120)

        # Drop down for start am/pm.
        self.dropDownMenu_start_ampm = OptionMenu(self.add_event_frame, self.dropdown_list[2], *ampm)
        self.dropDownMenu_start_ampm.config(background="ivory2", width=6)
        self.dropDownMenu_start_ampm.place(x=270, y=120)

        # finish times
        self.dropdown_list[3] = StringVar(self.add_event_frame)
        self.dropdown_list[3].set(hrs[0])
        if event:
            self.dropdown_list[3].set(event.end.hour % 12)

        self.dropdown_list[4] = StringVar(self.add_event_frame)
        self.dropdown_list[4].set(mins[0])
        if event:
            if event.end.minute != 0:
                self.dropdown_list[4].set(event.end.minute)

        self.dropdown_list[5] = StringVar(self.add_event_frame)
        self.dropdown_list[5].set(ampm[0])
        if event:
            if event.end.hour > 12: self.dropdown_list[5].set(ampm[1])

        self.dropDownMenu_fin_h = OptionMenu(self.add_event_frame, self.dropdown_list[3], *hrs)
        self.dropDownMenu_fin_h.config(background="ivory2", width=5)
        self.dropDownMenu_fin_h.place(x=150, y=180)

        self.dropDownMenu_fin_min = OptionMenu(self.add_event_frame, self.dropdown_list[4], *mins)
        self.dropDownMenu_fin_min.config(background="ivory2", width=5)
        self.dropDownMenu_fin_min.place(x=210, y=180)

        self.dropDownMenu_fin_ampm = OptionMenu(self.add_event_frame, self.dropdown_list[5], *ampm)
        self.dropDownMenu_fin_ampm.config(background="ivory2", width=6)
        self.dropDownMenu_fin_ampm.place(x=270, y=180)
        # end start and finish times

        # Title:
        self.entry_list[0] = Entry(self.add_event_frame, width=40, highlightbackground="ivory2")
        self.entry_list[0].place(x=150, y=240)
        self.entry_list[0].config(textvariable=title)

        # Location
        self.entry_list[1] = Entry(self.add_event_frame, width=40, highlightbackground="ivory2")
        self.entry_list[1].place(x=150, y=300)
        self.entry_list[1].config(textvariable=location)

        # Description
        self.entry_list[2] = Entry(self.add_event_frame, width=40, highlightbackground="ivory2")
        self.entry_list[2].place(x=150, y=360)
        self.entry_list[2].config(textvariable=description)

        # Notes
        self.entry_list[3] = Entry(self.add_event_frame, width=40, highlightbackground="ivory2")
        self.entry_list[3].place(x=150, y=420)
        self.entry_list[3].config(textvariable=notes)

        # end entry boxes
        # buttons

        # if the event is passed, we can delete and edit the event
        if event:
            self.done_button = Button(self.add_event_frame, command=lambda: self.event_frame_done_button(event),
                                 text="Submit", width=9, highlightbackground="ivory2")
            self.done_button.place(x=30, y=550) # Click this button when done editing

            self.delete_button = Button(self.add_event_frame, command=lambda: self.delete_event_button(event),
                                   text="Delete", width=9, highlightbackground="ivory2")
            self.delete_button.place(x=220, y=550) # Click this button when deleting

        # If None is passed, we are adding an event
        else:
            self.done_button = Button(self.add_event_frame, command=lambda: self.event_frame_done_button(),
                                 text="Submit", width=9, highlightbackground="ivory2")
            self.done_button.place(x=30, y=550) # Click this button when adding

        # Cancel button exists at any time when on this frame
        self.cancel_button = Button(self.add_event_frame, command=lambda: self.event_window_close(), text="Cancel", width=9,
                               highlightbackground="ivory2")
        self.cancel_button.place(x=410, y=550)

        # Set the class variable add event frame exists to True so other function don't make this frame again
        self.add_event_frame_exists = True

    def create_login_frame(self):
        """
        Initializes the frame that appears when a user first starts the application
        This frame allows the input of a username and password, 
        and two buttons; Create User and Login
        """
        self.login_frame = Frame(self.main_frame, bg="ivory3")
        self.login_frame.pack(fill="both", expand=True, padx=300, pady=200)

        self.USERNAME_ENTRY = Entry(self.login_frame, highlightbackground="ivory3")
        self.PASSWORD_ENTRY = Entry(self.login_frame, highlightbackground="ivory3", show="*")
        self.SUBMIT_CREDENTIALS_button = Button(self.login_frame, text="Login", width=9, highlightbackground="ivory3")
        self.SUBMIT_CREDENTIALS_button.configure(command=lambda: self.try_login(self.USERNAME_ENTRY.get(),
                                                                                self.PASSWORD_ENTRY.get()))
        self.CREATE_USER_button = Button(self.login_frame, text="Create User", width=9, highlightbackground="ivory3")
        self.CREATE_USER_button.configure(command=lambda: self.create_user(self.USERNAME_ENTRY.get(),
                                                                           self.PASSWORD_ENTRY.get()))
        self.LOGIN_ERROR_LABEL = Label(self.login_frame, text="Welcome", bg="ivory3")

        self.LOGIN_ERROR_LABEL.pack(fill="both", expand=True, padx=30, pady=10)
        self.USERNAME_ENTRY.pack(fill="both", expand=True, padx=40, pady=10)
        self.PASSWORD_ENTRY.pack(fill="both", expand=True, padx=40, pady=10)
        self.SUBMIT_CREDENTIALS_button.pack(side=RIGHT, padx=40, pady=20)
        self.CREATE_USER_button.pack(side=LEFT, padx=40, pady=20)

    def forward(self):
        """
        forward function is implemented by the forward button,
        when pressed, it shows the next month's content

        """
        global monthCounter, yearCounter

        # increment montcounter and yearcounter accordingly
        if monthCounter == 12: # When month counter reaches 12, it'll be reset to 1, because we only have 12 months
            monthCounter = 1
            yearCounter += 1 # Year Counter though, keeps being added to
        else:
            monthCounter += 1

        first_day_num_days = caltime.days(monthCounter, yearCounter) # get the tuple of first day and number of days
        															 # to start the calendar
        															 # [0] := first day
        															 # [1] := num days
        self.destroy_calendar_frame()			
        self.create_calendar_frame(monthCounter, first_day_num_days[0], first_day_num_days[1])

    def back(self):
        """
        back function is implemented by the back button,
        when pressed, it shows the next month's content

        """
        global monthCounter, yearCounter

        # decrement month and year counter accordingly
        if monthCounter == 1: # When month counter reaches 1, it'll be reset to 12, because we don't have negative months
            monthCounter = 12
            yearCounter -= 1 # Year Counter though, keeps being decremented
        else:
            monthCounter -= 1

        first_day_num_days = caltime.days(monthCounter, yearCounter) # get the tuple of first day and number of days
        															 # to start the calendar
        															 # [0] := first day
        															 # [1] := num days
        self.destroy_calendar_frame()
        self.create_calendar_frame(monthCounter, first_day_num_days[0], first_day_num_days[1])

    def day_clicked(self, button, month):
        """
        method calss, it will be invoked when the days of the calender are clicked
        it takes an int argument, the day of the month is passed to it to be shown

        args:	Button type button(calendar button clicked on)
        		String month (month of the calendar button clicked on)
        """

        global monthCounter, yearCounter, days, dayCounter, selected_button_month, selected_button_year, selected_button, todayOrSelectedDay


        first_day_num_days = caltime.days(month, yearCounter) # Local variable (tuple), 
        													  # [0] := first day of month passed and year the calendar is on, 
        													  # [1] := num days of month passed and year the calendar is on
        j = days.index(first_day_num_days[0]) # Take the index of the first day

        # Calculating the row and column of the button clicked on in the grid
        # x := ROW, y := COLUMN
        x = int(button.grid_info()['row']) - 1 
        y = int(button.grid_info()['column']) + 1

        dayCounter = (x * 7 + y) - j # This algorithm calculates the day that the button clicked on is
        							 # Based on row, column in the grid and the index of the first day in month
        							 # and stores it in global variable dayCounter

        selected_button_year = yearCounter # Global variable takes the year that the calendar is on
        selected_button_month = monthCounter # Global variable takes the month that the calendar is on
        #following is a tuple that takes the row and column of the selected button
        #it will be used in calendar frame to color the selected day
        selected_button = (x+1, y-1) # global tuple takes the row and column, inclrement row and decrement column for calculations in create calendar

        evs = [] # local list, it will take the events (String) of the specified date
        if self.event_days:
            for i in self.event_days:
                evs.append(str(i[0]))
        # Following will set the color of the selected button to a khaki color
        # and will reset the color of the previously selected button back to its original color
        # If the previously selected button is today, will set the color back to light blue
        if self.previous_button['text'] == str(self.current_day):
            self.previous_button.configure(bg="PaleTurquoise1", highlightbackground="PaleTurquoise1")
        # If the previously selected button has events, set it's color to bright yellow
        elif self.previous_button['text'] in evs:
            self.previous_button.configure(bg="light goldenrod yellow", highlightbackground="light goldenrod yellow")
        # Otherwise set it to default white color
        else:
            self.previous_button.configure(bg="white", highlightbackground="white")
        button.configure(bg="khaki", highlightbackground="khaki")
        self.previous_button = button # Set the previously selected button to the selected button,
        							  # Because now we are done working on selected buttons information
        							  # and have to keep track of it for future calculations
        # end

        self.destroy_events_frame() 
        todayOrSelectedDay = "Selected Day" # Now we have selected a day, so the label in events frame will read "Selected Day ..."
        self.create_events_frame(self.event_map.events_in_day(yearCounter, monthCounter, dayCounter), str(dayCounter),
                                 monthCounter, str(yearCounter)) # Create the frame of the month that the user is on

    def create_calendar_frame(self, current_month, first_day_of_month, num_days):
        """
        class method creates the calendar
        args:   int thisMonth, checks if this value is equal to current_months value
                int current_month,
                string first_day_of_month (the week day that the 1st day of month falls in)
        """
        global days, months, yearCounter, dayCounter, selected_button_year, selected_button_month, selected_button
        # make two frames that will go into calender frame
        self.cal_subframe1 = Frame(self.calendar_frame, width=604, height=88, background="ivory2")
        self.cal_subframe2 = Frame(self.calendar_frame, width=604, height=532, background="ivory2")
        self.cal_subframe1.grid(row=0, column=0, sticky=S)
        self.cal_subframe2.grid(row=1, column=0, sticky=N)

        # Local variable Back button to go to the previous month
        backButton = Button(self.cal_subframe1, text="Back", highlightbackground="ivory2")
        backButton.configure(command=lambda: self.back())
        backButton.place(x=20, y=30, width=100, height=25)

        monthName = Label(self.cal_subframe1, text=months[current_month - 1] + " " + str(yearCounter),
                          background="ivory2")
        monthName.place(x=120, y=0, width=364, height=88)

        # Local variable Forward button to go to the next month
        forwardButton = Button(self.cal_subframe1, text="Forward", highlightbackground="ivory2")
        forwardButton.configure(command=lambda: self.forward())
        forwardButton.place(x=484, y=30, width=100, height=25)

        # Local variabel where all the buttons go
        btn = [[Label() for x in range(7)] for y in range(7)] # This is a 2D list, every row holds 7 lists of 7 buttons
        													   # Some of these won't take any values 
        													   # but there are some months that we need 6 rows
        													   # since this is a local variable and will be popped of the
        													   # stack once function goes out of scope, we won't have too 
        													   # much overhead
        # index to keep track of the days
        i = 1
        j = days.index(first_day_of_month) # Local variabel to find the index of the first day of month
        #holds the previously selected button, We do this to keep track of the selected buttons for coloring purposes,
        # it will be used in the day clicked function
        self.previous_button = btn[0][0]

        # Taking all the days with the events in them
        self.event_days = self.event_map.events_in_month(yearCounter, monthCounter)        
            
        # Maps days to the first row
        for col in range(7):
            entry = Label(self.cal_subframe2, width=8, height=4, text=days[col], bg="grey25", fg="snow")
            entry.grid(row=0, column=col, sticky=W + E + S + N, padx=1, pady=1)

        # Maps days to the 2nd - 5th rows
        for col in range(7):
        	# If the col is less than the index of first day of month, fill the area with empty boxes
        	# So for example, if the index of first day is 5, empty boxes will show from 0-4 
            if col < j:
                empty_box = Label(self.cal_subframe2, width=5, height=3, bg="white", highlightbackground="white")
                empty_box.grid(row=1, column=col, sticky=W + E + S + N, padx=1, pady=1)
            # The rest of the first column of the calendar will be filled with buttons
            else:
                # Check to see if the month and year that we're on is todays montha nd year, 
                # if so the current day will be highlighted
                if current_month == self.current_month and yearCounter == self.current_year:
                    if i == self.current_day:
                        btn[0][col] = Label(self.cal_subframe2, width=5, height=3, text=str(i),
                                             bg="PaleTurquoise1",
                                                   highlightbackground="PaleTurquoise1")
                        btn[0][col].grid(row=1, column=col, sticky=W + E + S + N, padx=1, pady=1)
                        btn[0][col].bind("<Button-1>", lambda e,m=btn[0][col], n=current_month: self.day_clicked(m, n))

                    else:
                        btn[0][col] = Label(self.cal_subframe2, width=5, height=3, text=str(i), bg="white",
                                             highlightbackground="white")
                        btn[0][col].grid(row=1, column=col, sticky=W + E + S + N, padx=1, pady=1)
                        btn[0][col].bind("<Button-1>", lambda e,m=btn[0][col], n=current_month: self.day_clicked(m, n))


                else:
                    btn[0][col] = Label(self.cal_subframe2, width=5, height=3, text=str(i), bg="white",
                                         highlightbackground="white")
                    btn[0][col].grid(row=1, column=col, sticky=W + E + S + N, padx=1, pady=1)
                    btn[0][col].bind("<Button-1>", lambda e,m=btn[0][col], n=current_month: self.day_clicked(m, n))
                i += 1

        # The 2nd to the last row of the calendar
        for row in range(2, 7):
            for col in range(7):

            	# Check if the index of the day is more than number of days 
            	# If it is then the rest of the row will be filled with empty boxes
                if i > num_days:
                    empty_box = Label(self.cal_subframe2, width=5, height=3, bg="white", highlightbackground="white")
                    empty_box.grid(row=row, column=col, sticky=W + E + S + N, padx=1, pady=1)
                else:
                    # the day that we're on is highlighted
                    if current_month == self.current_month and yearCounter == self.current_year:
                        if i == self.current_day:
                            btn[row][col] = Label(self.cal_subframe2, width=5, height=3, text=str(i),
                                                   bg="PaleTurquoise1",
                                                   highlightbackground="PaleTurquoise1")
                            btn[row][col].grid(row=row, column=col, sticky=W + E + S + N, padx=1, pady=1)
                            btn[row][col].bind("<Button-1>", lambda e,m=btn[row][col], n=current_month: self.day_clicked(m, n))
                        else:
                            btn[row][col] = Label(self.cal_subframe2, width=5, height=3, text=str(i), bg="white",
                                                   highlightbackground="white")
                            btn[row][col].grid(row=row, column=col, sticky=W + E + S + N, padx=1, pady=1)
                            btn[row][col].bind("<Button-1>", lambda e,m=btn[row][col], n=current_month: self.day_clicked(m, n))
                    else:
                        btn[row][col] = Label(self.cal_subframe2, width=5, height=3, text=str(i), bg="white",
                                               highlightbackground="white")
                        btn[row][col].grid(row=row, column=col, sticky=W + E + S + N, padx=1, pady=1)
                        btn[row][col].bind("<Button-1>", lambda e,m=btn[row][col], n=current_month: self.day_clicked(m, n))
                    i += 1

        # Coloring the days with events
        # Following list will keep track of days with events, it'll be used in day_clicked
        if self.event_days:
            for event in self.event_days:
                if event[0] != self.current_day:
                	# The following algorithm is used to find the index of the button that has events and color it
                    btn[0 if ((((event[0]+j) - 1) // 7) + 1) ==1 else ((((event[0]+j) - 1) // 7) + 1)][(((event[0]+j) % 7) - 1) if ((event[0]+j) % 7) != 0 else
                        (((event[0]+j) % 7) + 6)].configure(bg="light goldenrod yellow", highlightbackground="light goldenrod yellow")

        # Set the color of the selected button to khaki
        if current_month == selected_button_month and yearCounter == selected_button_year:
            if selected_button != None:
            	# The following algorithm is used to find the index of the button that is selected and color it
                self.previous_button = btn[0 if selected_button[0]==1 else selected_button[0]][selected_button[1]]
                self.previous_button.configure(bg= "khaki", highlightbackground= "khaki")


    def create_events_frame(self, today_events, current_day, current_month, current_year):
        """
        class method creates the events frame
        args:   array of event objects: today_events
                int current_day
                int current_month
                int current_year
        """
        global todayOrSelectedDay
        # Event_frame subframes
        self.today_events_subframe = Frame(self.events_frame, width=390, height=540, background="ivory3")
        self.event_buttons_subframe = Frame(self.events_frame, width=390, height=80, background="ivory3")

        self.today_events_subframe.grid(row=0, column=0)
        self.event_buttons_subframe.grid(row=1, column=0)

        # This label will show the selected days date / todays date
        self.todayLabel = Label(self.today_events_subframe, text="{}:     {} {}, {}".format(todayOrSelectedDay,
            months[current_month - 1], current_day, current_year), bg="grey25", fg="snow", width=38)
        self.todayLabel.place(x=20, y=10)
        scrollbar = Scrollbar(self.today_events_subframe)# Set up a scroll bar
        # Set up a listbox to show the events in
        self.listbox = Text(self.today_events_subframe, bg="ivory3", highlightbackground="ivory3", width=46, height=28,
                            yscrollcommand=scrollbar.set)
        self.listbox.place(x=20, y=50)


        if today_events is not None:
            for cur_event in today_events:
                title = cur_event.title # Local variable, From the event passed to the argument, get title
                start = cur_event.start.format('dddd, MMMM D, h:mm a') # Local variable, From the event passed to the argument, get start time
                location = cur_event.location # Local variable, From the event passed to the argument, get location
                event_text = "{}\n{}\n{}".format(title, start, location) # Local string, concatenation of title, start and location
                event_button = Label(self.listbox, text=event_text, relief="groove", width=35, height=4,
                                      bg="ivory3", highlightbackground="ivory2") # Create a local label reading event_text
                event_button.bind("<Enter>", lambda e: e.widget.config(bg="ivory2")) # When you mouse over the label it changes color to ivory2
                event_button.bind("<Leave>", lambda e: e.widget.config(bg="ivory3")) # When you remove the curser from it, it changes color to ivory3

                event_button.bind("<Button-1>", lambda e,x = cur_event: self.toggle_event_frame(x))# Assign the function toggle event frame to the label
                self.listbox.window_create(END, window=event_button)

        scrollbar.place(in_=self.listbox, relx=1.0, relheight=1.0, bordermode="outside") # Put scrollbar right next to the Listbox
        scrollbar.config(command=self.listbox.yview)
        self.listbox.config(state=DISABLED, cursor="arrow")

        add_event_button = Button(self.event_buttons_subframe, width=9, text="Add Event", highlightbackground="ivory3")
        add_event_button.configure(command=lambda: self.toggle_event_frame())
        add_event_button.place(x=140, y=10)

    def create_main_menu(self, current_day, current_month, current_year, first_day_of_month, num_days):
        """
        Create the main menu.
        :int current_day:
        :int current_month:
        :int current_year:
        :string first_day_of_month:
        :int num_days:
        """

        # Following variables define calendar and events frames
        self.calendar_frame = Frame(self.main_frame, width=604, height=620, background="ivory2")
        self.calendar_frame.grid(row=0, column=0, sticky=W + N + S, padx=(10, 10), pady=(10, 10))

        self.events_frame = Frame(self.main_frame, width=390, height=620, background="ivory3")
        self.events_frame.grid(row=0, column=1, sticky=N + S + E, pady=(10, 10))

        self.create_calendar_frame(current_month, first_day_of_month, num_days)
        self.create_events_frame(self.event_map.events_in_day(current_year, current_month, current_day),
                                 current_day, current_month, current_year)

    def mask_event_buttons(self):
        """
        used to hide the buttons on the events frame
        """
        self.mask_buttons_subframe = Frame(self.events_frame, width=390, height=80, background="ivory3")
        self.mask_buttons_subframe.grid(row=1, column=0)

    def destroy_mask_event_buttons(self):
        """
        used to remove the mask over buttons
        """
        if self.mask_buttons_subframe.winfo_exists() == 1:
            self.mask_buttons_subframe.destroy()

    def destroy_calendar_frame(self):
        """
        class method destroys the clendar frame
        """
        # check if clanedar subframes exist, if they do destroy them
        if self.cal_subframe1.winfo_exists() == 1:
            self.cal_subframe1.destroy()
        if self.cal_subframe2.winfo_exists() == 1:
            self.cal_subframe2.destroy()

    def destroy_events_frame(self):
        """
        class method destroys events frame
        """
        # Check if the event subframes exist, if they do destroy them
        if self.today_events_subframe.winfo_exists() == 1:
            self.today_events_subframe.destroy()
        if self.event_buttons_subframe.winfo_exists() == 1:
            self.event_buttons_subframe.destroy()

    def destroy_main_menu(self):
        """
        class method destroys main menu
        """
        self.destroy_calendar_frame()
        self.destroy_events_frame()
        # check if the calendar and event frames exist, if they do, destroy them
        if self.calendar_frame.winfo_exists() == 1:
            self.calendar_frame.destroy()
        if self.events_frame.winfo_exists() == 1:
            self.events_frame.destroy()

    def __init__(self, parent):

        global monthCounter, yearCounter, days, months, dayCounter, selected_button_month, selected_button_year, selected_button, todayOrSelectedDay

        self.main_frame = parent
        self.event_map = 0 # This variable will hold the event_map, it will take the event map once logged in, in line 41
        date = caltime.today_ymd() # Calls the backend function today_ymd to get todays date
        first_day_num_days = caltime.days(date[1], date[0]) # Calls the backend function days, 
                                                            # to get a tuple of first day of current month 
                                                            # and number of days in current month
        self.current_month = monthCounter = date[1] # Set current month
        self.current_day = dayCounter = date[2] # Set current day
        self.current_year = yearCounter = date[0] # Set current year
        self.first_day_of_month = first_day_num_days[0] # Set first day of current month
        self.num_days_in_month = first_day_num_days[1] # Set number of days of current month
        
        selected_button_month = monthCounter # Initialize the selected buttons month with the value of monthCounter
        selected_button_year = yearCounter # Initialize the selected buttons month with the value of yearCounter
        selected_button = None # Mark if we have a selected button, upon startup, this is None, 
                               # but once the user selects a button, it will take its value
        todayOrSelectedDay = "Today" # This is for the label on the events frame, upon start up, it reads "Today",
                                     # But once the user presses a button, it will change its value to "Selected Day"

        # Init items to none so their existence can be checked later.
        self.windowlabel = None
        self.done_button = None # Will be set to Done button in toggle add events function
        self.delete_button = None # Will be set to Delete button in toggle add events function
        self.cancel_button = None # Will be set to Cancel button in toggle add events function
        self.dropDownMenu_d = None # Will be set to OptionMenu of day in toggle add events function
        self.dropDownMenu_y = None # Will be set to OptionMenu of year in toggle add events function
        self.dropDownMenu_m = None # Will be set to OptionMenu of month in toggle add events function
        self.dropDownMenu_start_h = None # Will be set to OptionMenu of start times hour in toggle add events function
        self.dropDownMenu_start_min = None # Will be set to OptionMenu of start times minute in toggle add events function
        self.dropDownMenu_start_ampm = None # Will be set to OptionMenu of start times am/pm in toggle add events function
        self.dropDownMenu_fin_h = None # Will be set to OptionMenu of finish times hour in toggle add events function
        self.dropDownMenu_fin_min = None # Will be set to OptionMenu of finish times minute in toggle add events function
        self.dropDownMenu_fin_ampm = None # Will be set to OptionMenu of finish times am/pm in toggle add events function
        self.add_event_frame_exists = False # Mark if the add events frame is created

        self.create_login_frame() # First function that will be called to start the program, user needs to log in


def display_about(root):
    """
    Called when selecting about from the help menu dropdown.
    Displays information about the project, such as author names
    """
    top = Toplevel(root)
    Label(top, text="Secure Calendar Application" + os.linesep +
                    "By Ashton Shears, Marc Lee, Parsa Bagheri, Quinn Milionis, and Sam Champer" + os.linesep +
                    "Created as a project for CIS 422 at the University of Oregon").pack()


def display_help(root):
    """
    Called when selecting 'Display Help' from the help menu dropdown.
    Displays a helpful guide to explain how to use the program.
    """
    top = Toplevel(root)
    Label(top, text="SecureCal user quick start guide:" + os.linesep +
            "Access:" + os.linesep + 
            "New User: Enter user ID-> type password (1-32 characters)->Press Create User Button" + os.linesep +
            "Existing User: Enter user ID-> type correct password -> Press Login Button" + os.linesep + os.linesep +
            "Changing Month: Press Back/Forward Buttons located next to month" + os.linesep + os.linesep +
            "Add Events: Press Add Event-> Enter Event info-> Press Done Button" + os.linesep + os.linesep +
            "Edit Events: Select an existing Event-> Update information -> Press Submit Button" + os.linesep + os.linesep+
            "Delete Events: Select Event-> Press Delete Button" + os.linesep + os.linesep +
            "Import Calendar: Press File(top left corner)->Select 'Import unencrypted tsv' from drop-down->choose file to import" + os.linesep + os.linesep +
            "Export Calendar: Press File (top left corner)-> Select 'Export to unencrypted tsv' from drop-down" + os.linesep + os.linesep +
            "Save Calendar: Press File (top left corner)-> Select 'Save' from drop-down" + os.linesep + os.linesep +
            "Delete Calendar: Press File (top left corner)-> Select 'Delete Calendar' from dropdown" + os.linesep + os.linesep+
            "Logout: Press File (top left corner) -> Select 'Logout' from drop-down", justify=LEFT).pack()


def delete_calendar(cal):
    """
    Called when selecting 'Delete Calendar' from the file menu dropdown.
    Deletes all user info and returns to the login frame
    """
    result = messagebox.askquestion("Delete Calendar", "Are you sure you want to delete this calendar?" + os.linesep +
                                        "All data will be erased permanently", icon='warning')
    if result == 'yes':
        cal.destroy_main_menu()
        cal.event_map.delete_user()
        cal.__init__(cal.main_frame)
        menubar.entryconfig("File", state="disabled") # While user is not logged in, Menu bar items are disabled i.e. not clickable


def delete_main_menu_and_toggle_login_screen(cal):
    """
    Called when the user selects logout from the file menu dropdown
    """
    if cal.event_map.changed:
        result = messagebox.askquestion("Unsaved Changes", "There are unsaved changes to this calendar." + os.linesep +
                                        "Are you sure you want to exit?", icon='warning')
        if result != 'yes':
            return
    cal.destroy_main_menu()
    cal.__init__(cal.main_frame)
    menubar.entryconfig("File", state="disabled")


def delete_window(root, cal):
    """
    Called when the user clicks the X at the top right of the application or the exit option from the file menu.
    """
    if cal.event_map == 0:
        root.destroy()
    elif cal.event_map.changed:
        result = messagebox.askquestion("Unsaved Changes", "There are unsaved changes to this calendar." + os.linesep +
                                        "Are you sure you want to exit?", icon='warning')
        if result == 'yes':
            root.destroy()
    else:
        root.destroy()


#################
# INITILAIZE GUI#
#################
if __name__ == '__main__':
    global menubar
    root = Tk()
    root.geometry('1024x640')# Set the size of the scree
    root.resizable(width=False, height=False) # make it so that it's not resizable
    root.config(bg="ivory2") # color it
    root.title('SecureCal') # name it
    app = Calendar(root)
    menubar = Menu(root) # top bar menu
    # Create a pulldown menu, and add it to the menu bar
    filemenu = Menu(menubar, tearoff=0)
    filemenu.add_command(label="Save", command=lambda: app.event_map.write_encrypted()) 
    filemenu.add_command(label="Import unencrypted tsv",
                         command=lambda: app.event_map.read_tsv(filedialog.askopenfilename()))
    filemenu.add_command(label="Export to unencrypted tsv", command=lambda: app.event_map.write_tsv())
    filemenu.add_command(label="Logout", command=lambda: delete_main_menu_and_toggle_login_screen(app))
    filemenu.add_command(label="Delete User Account", command=lambda: delete_calendar(app))
    filemenu.add_command(label="Exit", command=lambda: delete_window(root, app))
    menubar.add_cascade(label="File", menu=filemenu)
    # Create help menu
    helpmenu = Menu(menubar, tearoff=0)
    helpmenu.add_command(label="About", command=lambda: display_about(root))
    helpmenu.add_command(label="Display Help", command=lambda: display_help(root))
    menubar.add_cascade(label="Help", menu=helpmenu)
    root.config(menu=menubar)
    menubar.entryconfig("File", state="disabled")

    root.protocol("WM_DELETE_WINDOW", lambda: delete_window(root, app))
    root.mainloop()
