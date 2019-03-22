# Backend functions for secure calendar.

import arrow  # For handling dates/times.
import crypt  # For reading from and writing to encrypted CSV files.
import csv  # For convenient reading of csv files.
import os  # For operating specific newline char.


class CalEvent:
    # A class for events to make accessing elements convenient.
    def __init__(self, title, start, end, location, description, notes):
        """
        All args are strings.
        start and end should be 'MMMM D, YYYY, h:mm a' formated strings (month, day, year, hour:minute am/pm).
        """
        self.title = title
        self.start = arrow.get(start, 'MMMM D, YYYY, h:mm a')
        self.end = arrow.get(end, 'MMMM D, YYYY, h:mm a')
        self.location = location
        self.description = description
        self.notes = notes

    def app_str(self):
        # A string for printing into the event list in the calendar.
        return "{}Start Time: {}End Time: {}" \
               "Description: {}" \
               "Location: {}Notes: {}" \
                .format(self.title + os.linesep,
                        self.start.format('dddd, MMMM D, h:mm a') + os.linesep,
                        self.end.format('dddd, MMMM D, h:mm a') + os.linesep,
                        self.location + os.linesep,
                        self.description + os.linesep,
                        self.notes)

    def tsv_str(self):
        # A string for writing events to the csv file:
        return "{}\t{}\t{}\t{}\t{}\t{}" \
               .format(self.title,
                       self.start.format('MMMM D, YYYY, h:mm a'),
                       self.end.format('MMMM D, YYYY, h:mm a'),
                       self.location,
                       self.description,
                       self.notes)

    def __str__(self):
        # Function for representing events in the console, mostly for debugging.
        return self.tsv_str()

    def __repr__(self):
        # Function for representing events in the console, mostly for debugging.
        return self.tsv_str()


class EventMap:
    # A class storing all of a user's events.
    def __init__(self, username, password):
        """
        The internal data structure for storing calendar events.
        :param username: a username
        :param password: the associated password
        """
        self.e_map = dict()  # The root of the data structure to store events.
        self._username = username
        self._password = password
        self.error = 0
        self.changed = False  # User will be prompted to save unsaved data based on this variable.

        # The map is initialised with the events present in the .cal file associated
        # with the username and password. First, make a python list from the contents of the file:
        raw_list = crypt.decrypt_and_get_list(username, password)
        if raw_list == -1:
            self.error = 1
        elif isinstance(raw_list, list):
            # Each entry in the raw list must be converted to a CalEvent object and then added to the map.
            for i in raw_list:
                cur_event = CalEvent(i[0], i[1], i[2], i[3], i[4], i[5])
                self.add(cur_event)
        self.changed = False  # After adding the initial events, mark that the calendar has not been changed.

    def add(self, event):
        # Add an event to the event map.
        # Since map is indexed by year, month, and day, find the ymd of the event we are adding:
        year = event.start.year
        month = event.start.month
        day = event.start.day

        # If there are no events in the year, month, or day of the event being added, add that day to the map:
        if year not in self.e_map:
            self.e_map[year] = dict()
        if month not in self.e_map[year]:
            self.e_map[year][month] = dict()
        if day not in self.e_map[year][month]:
            self.e_map[year][month][day] = []

        # Prevent duplicate events:
        for i in self.e_map[year][month][day]:
            if i.title == event.title:
                return "error"
        # Add the event to the list for the associated day:
        self.e_map[year][month][day].append(event)
        self.changed = True  # Mark that the calendar has been changed.

    def events_in_month(self, year, month):
        """
        Return a list of days with events in a given month.
        :param year: as an int
        :param month: as an int
        :return: a list of tuples of the form:
            (day of the month, number of events on that day).
        """
        # If year or month are not in the map, return None.
        if year not in self.e_map:
            return None
        if month not in self.e_map[year]:
            return None
        days_with_events = []
        # If the month is in the map, index through the month:
        for i in self.e_map[year][month]:
            # For each day in the month with events,
            # add a tuple consisting of that day and the number of events on it.
            days_with_events.append((i, len(self.e_map[year][month][i])))
        return days_with_events

    def events_in_day(self, year, month, day):
        """
        Return a list of events on a given day.
        :param year: as an int.
        :param month: as an int.
        :param day: as an int.
        :return: a list of events on the given day.
        """
        # Return none if the year, month, or day are not in the map:
        if year not in self.e_map:
            return None
        if month not in self.e_map[year]:
            return None
        if day not in self.e_map[year][month]:
            return None
        # If the ymd is in the event map, return a sorted list of all entries in that day:
        events = self.e_map[year][month][day]
        events.sort(key=lambda el: el.start)  # The list is sorted by start time.
        return events

    def pop(self, event):
        """
        Removes event from map.
        :param event: an event object
        """
        # Since map is indexed by year, month, and day, find the ymd of the event we are removing:
        year = event.start.year
        month = event.start.month
        day = event.start.day
        # Index to that ymd, then remove the event.
        self.e_map[year][month][day] = [i for i in self.e_map[year][month][day] if i.title != event.title]
        if not self.e_map[year][month][day]:
            self.e_map[year][month].pop(day)
        if not self.e_map[year][month]:
            self.e_map[year].pop(month)
        if not self.e_map[year]:
            self.e_map.pop(year)
        
        
        self.changed = True  # Mark that the calendar has been changed.

    def write_encrypted(self):
        """
        Writes all events from the event map to the csv file.
        """
        # First write the header, which is decrypted in order to identify the .cal file as a correct file.
        write_str = "Title\tStart\tEnd\tLocation\tDescription\tNotes" + os.linesep
        # For each year, month, and then day in the event map, add all events to a string.
        for year in self.e_map:
            for month in self.e_map[year]:
                for day in self.e_map[year][month]:
                    for entry in self.e_map[year][month][day]:
                        # The string comprises the the tsv string for each event.
                        write_str += entry.tsv_str() + os.linesep
        # write_str now consists of all of the header and then all events in the event list,
        # write the completed write_str to the encrypted file associated with this user.
        crypt.encrypt_and_store(self._username, self._password, write_str)
        # Since changes have now been saved, we don't need to prompt users to save.
        self.changed = False

    def delete_user(self):
        # Delete a user from the system. Removes a user's .cal file.
        os.remove("{}.cal".format(self._username))
        # Manually call python garbage collector.
        del self.e_map
        del self._username
        del self._password

    def write_tsv(self):
        # Writes the event list to a non-encrypted tsv file.
        # First, get a list of all events in the calendar:
        events = []
        for year in self.e_map:
            for month in self.e_map[year]:
                for day in self.e_map[year][month]:
                    # Add all events on the day to the list:
                    events.extend(self.e_map[year][month][day])
        events.sort(key=lambda el: el.start)  # The list is sorted by start time.

        # Get the current year, month, and day for the the file name.
        now = arrow.now()
        filename = "{}-backup-{}-{}-{}.tsv".format(self._username, now.year, now.month, now.day)
        with open(filename, 'w') as f:
            if os.name != 'nt':  # For non-windows operating systems:
                # First write the header line:
                f.write("Title\tStart\tEnd\tLocation\tDescription\tNotes" + os.linesep)
                for event in events:
                    # Now write each event in the list:
                    f.write(event.tsv_str() + os.linesep)
            if os.name == 'nt':  # For windows, to compensate for unintended behavior of the write function:
                # First write the header line:
                f.write("Title\tStart\tEnd\tLocation\tDescription\tNotes\n")
                for event in events:
                    # Now write each event in the list:
                    f.write(event.tsv_str() + "\n")

    def read_tsv(self, filename):
        # Adds events read from a tsv file.
        # If the open file dialogue is cancelled out of, the function is passed None.
        if filename is None or filename == ():
            return
        with open(filename, "r") as f:
            # Read past the first (header) line, while checking for correctly formatted file:
            if f.readline() != "Title\tStart\tEnd\tLocation\tDescription\tNotes" + os.linesep:
                return "error"
            raw_list = list(csv.reader(f, delimiter='\t'))  # Add all lines from the file to a list.
        if len(raw_list) != 0:
            # Each entry in the raw list must be converted to a CalEvent object and then added to the map.
            for i in raw_list:
                # Incorrectly formatted files cannot be parsed by arrow.
                try:  # For incorrect file handling:
                    cur_event = CalEvent(i[0], i[1], i[2], i[3], i[4], i[5])
                    self.add(cur_event)
                except arrow.parser.ParserError:
                    continue

def new_user(username, password):
    # Function to create a new .cal file for a new user.
    crypt.encrypt_and_store(username, password, "Title\tStart\tEnd\tLocation\tDescription\tNotes" + os.linesep)
