# main.py
import os
import random
from PIL import Image
import constant
from datetime import datetime, timedelta
import re

import discord
from discord.ext import tasks
from dateutil import parser
from dotenv import load_dotenv

class RemindMe_Timer:
    def __init__(self,i,t,m,m_id,m_c,r_m):
        self.index = i
        self.time = t
        self.message = m
        self.message_id = m_id
        self.message_channel = m_c
        self.reply_message = r_m

RemindMe_Timers = []

async def read_timers_from_file():
    f = open('remindme_timers.txt', 'r')
    Lines = f.readlines()

    for line in Lines:
        if not line == "":
            line.strip()
            index = line.split(",")[0]
            message_time = datetime.strptime(line.split(",")[1], "%d-%b-%Y (%H:%M:%S.%f)")
            message_id = line.split(",")[2]
            message_channel = line.split(",")[3]
            reply_message = line.split(",")[4]

            channel = await client.fetch_channel(message_channel)
            message = await channel.fetch_message(message_id)
            new_timer = RemindMe_Timer(index,message_time,message,message_id,message_channel,reply_message)
            RemindMe_Timers.append(new_timer)

    f.close()

def write_timer_to_file(remindme_timer):
    f = open("remindme_timers.txt", "a")
    line_string = ""
    line_string += str(remindme_timer.index)
    line_string += ","
    line_string += remindme_timer.time.strftime("%d-%b-%Y (%H:%M:%S.%f)")
    line_string += ","
    line_string += str(remindme_timer.message_id)
    line_string += ","
    line_string += str(remindme_timer.message_channel)
    line_string += ","
    line_string += remindme_timer.reply_message
    line_string += "\n"
    f.write(line_string)
    f.close()

def remove_timer_to_file(remindme_timer):

    with open("remindme_timers.txt", "r") as f:
        lines = f.readlines()
    f.close()

    with open("remindme_timers.txt", "w") as f:
        for line in lines:
            line.strip()
            index = line.split(",")[0]
            if not int(index) == int(remindme_timer.index):
                f.write(line)
    f.close()

async def parse_remindme_message(message,user_message):
    compiled = re.compile(re.escape('remindme '), re.IGNORECASE)
    command = compiled.sub('',user_message)
    split = command.split(' ',2)

    command_correct = 1
    if len(split) >= 2:
        wait_time = split[0].strip()
        unit = split[1].strip().lower()

        if len(split) == 3:
            reply_message = split[2].strip()
        else:
            reply_message = ""

        if not wait_time.isdigit():
            command_correct = 0
        else:
            wait_time = int(wait_time)

        if unit not in constant.TIME_UNITS:
            command_correct = 0
    else:
        command_correct = 0

    if command_correct == 1:
        await start_remindme_timer(message,wait_time,unit,reply_message)
    else:
        await message.channel.send("Invalid Command")

# New Parser
async def new_parse_remindme_message(message,user_message):
    # remove remindme
    compiled = re.compile(re.escape('remindme '), re.IGNORECASE)
    command = compiled.sub('',user_message)

    parsing = 1
    can_process = 1
    command_no_timer = 0
    command_added = 0
    command_list = []
    command_list_original = []

    # date format regex
    number_date_regex = re.compile("\d*[\/|-]\d*[\/|-]\d*")
    full_time_regex = re.compile("\d{2}:\d\d")

    message_time = ""
    reply_message = ""
 
    while parsing:
        # determine next 3 splits
        split = command.split(' ',2)
        for command in split:
            command_list.append(command.lower())
            command_list_original.append(command)

        # Found Last 1 Command
        if len(command_list) == 1:
            if command_list[0] == "total":
                await message.channel.send("There are " + str(len(RemindMe_Timers)) + " active reminders")
                command_no_timer = 1
                can_process = 0
                parsing = 0
            elif number_date_regex.match(command_list[0]):
                if command_added == 0:
                    # Slash Date No Message
                    message_time = parser.parse(command_list[0])

                    # Add 9am time
                    message_time = message_time + timedelta(hours=9)
                    reply_message = "<@" + str(message.author.id) + ">"
                    can_process = 1
                    parsing = 0
                else:
                    can_process = 1
                    parsing = 0
            elif any(ext in command_list[0] for ext in constant.AM_PM_LIST):

                for ending in constant.AM_PM_LIST:
                    if ending in command_list[0]:
                        am_pm = ending

                time_to_add = command_list[0].split(am_pm)[0]
                if time_to_add.isdigit():
                    time_to_add = int(time_to_add)
                    if am_pm == 'am':
                        time_to_add = time_to_add
                    else:
                        if time_to_add == 12:
                            time_to_add = 12
                        else:
                            time_to_add = time_to_add + 12
                    if time_to_add > 24:
                        can_process = 0
                        parsing = 0
                    else:
                        if command_added == 0:
                            message_time = datetime.now().replace(hour=time_to_add)
                            reply_message = "<@" + str(message.author.id) + ">"
                            can_process = 1
                            parsing = 0
                        else:
                            message_time = message_time.replace(hour=time_to_add)
                            reply_message = "<@" + str(message.author.id) + ">"
                            can_process = 1
                            parsing = 0

                elif full_time_regex.match(time_to_add):
                    new_hour = time_to_add.split(':')[0]
                    new_minute = time_to_add.split(':')[1]
                    if new_hour.isdigit() and new_minute.isdigit():
                        new_hour = int(new_hour)
                        new_minute = int(new_minute)
                        if am_pm == 'am':
                            new_hour = new_hour
                        else:
                            if new_hour == 12:
                                new_hour = new_hour
                            else:
                                new_hour = new_hour + 12
                        if new_hour > 24:
                            can_process = 0
                            parsing = 0
                        else:
                            if command_added == 0:
                                message_time = datetime.now()
                                message_time = message_time.replace(hour=new_hour)
                                message_time = message_time.replace(minute=new_minute)
                                reply_message = "<@" + str(message.author.id) + ">"
                                can_process = 1
                                parsing = 0
                            else:
                                message_time = message_time.replace(hour=new_hour)
                                message_time = message_time.replace(minute=new_minute)
                                reply_message = "<@" + str(message.author.id) + ">"
                                can_process = 1
                                parsing = 0
                    else:
                        can_process = 0
                        parsing = 0
                else:
                    can_process = 0
                    parsing = 0

            elif command_list[0] in constant.MONTH_LIST:
                # Month being added
                message_time = await add_time_to_date(message_time,command_list[0],'month')
                if command_added == 0:
                    message_time = message_time.replace(day=1)
                reply_message = "<@" + str(message.author.id) + ">"
                can_process = 1
                parsing = 0

            elif command_list[0].isdigit():
                if len(command_list[0]) == 2 or  len(command_list[0]) == 4:
                    message_time = await add_time_to_date(message_time,command_list[0],'year')
                    if command_added == 0:
                        message_time = message_time.replace(day=1,month=1)
                    reply_message = "<@" + str(message.author.id) + ">"
                    can_process = 1
                    parsing = 0
                else:
                    can_process = 0
                    parsing = 0

            elif any(ext in command_list[0] for ext in constant.DAY_ENDINGS):
                date = ''
                for day_ending in constant.DAY_ENDINGS:
                    if day_ending in command_list[0]:
                        date = command_list[0].replace(day_ending,'')
                if date.isdigit():
                    message_time = await add_time_to_date(message_time,date,'day')
                    reply_message = "<@" + str(message.author.id) + ">"
                    can_process = 1
                    parsing = 0
                elif command_added == 0:
                    can_process = 0
                    parsing = 0
                else:
                    reply_message = command_list_original[0] + ' ' + command_list_original[1] + ' ' + command_list_original[2] 
                    can_process = 1
                    parsing = 0

            elif any(ext in command_list[0] for ext in constant.TIME_UNITS):
                time_to_add = 0
                unit_to_add = ""
                for unit in constant.TIME_UNITS:
                    if unit in command_list[0]:
                        time_to_add = command_list[0].replace(unit,'')
                        unit_to_add = unit
                if time_to_add.isdigit():
                    if command_added == 0:
                        message_time = datetime.now()
                        message_time = await add_time(message_time,time_to_add,unit_to_add)
                        reply_message = "<@" + str(message.author.id) + ">"
                        can_process = 1
                        parsing = 0
                    else:
                        message_time = await add_time(message_time,time_to_add,unit_to_add)
                        reply_message = "<@" + str(message.author.id) + ">"
                        can_process = 1
                        parsing = 0
                elif command_added == 0:
                    can_process = 0
                    parsing = 0
                else:
                    reply_message = command_list_original[0]
                    can_process = 1
                    parsing = 0

            elif command_added == 0:
                can_process = 0
                parsing = 0
            else:
                # Last command is message
                reply_message = command_list_original[0]
                can_process = 1
                parsing = 0

        # Found Last 2 commands
        elif len(command_list) == 2:
            if command_list[0].isdigit() and command_list[1] in constant.TIME_UNITS:
                if command_added == 0:
                    message_time = datetime.now()
                    message_time = await add_time(message_time,command_list[0],command_list[1])
                    reply_message = "<@" + str(message.author.id) + ">"
                    can_process = 1
                    parsing = 0
                else:
                    message_time = await add_time(message_time,command_list[0],command_list[1])
                    reply_message = "<@" + str(message.author.id) + ">"
                    can_process = 1
                    parsing = 0
            elif command_list[0] in constant.MONTH_LIST:
                # Month being added
                message_time = await add_time_to_date(message_time,command_list[0],'month')
                command_added = 1
                command = command_list_original[1]
                command_list.clear()
                command_list_original.clear()

            elif command_list[0].isdigit():
                message_time = await add_time_to_date(message_time,command_list[0],'day')
                command_added = 1
                command = command_list_original[1]
                command_list.clear()
                command_list_original.clear()

            elif any(ext in command_list[0] for ext in constant.DAY_ENDINGS):
                date = ''
                for day_ending in constant.DAY_ENDINGS:
                    if day_ending in command_list[0]:
                        date = command_list[0].replace(day_ending,'')
                if date.isdigit():
                    message_time = await add_time_to_date(message_time,date,'day')
                    command_added = 1
                    command = command_list_original[1]
                    command_list.clear()
                    command_list_original.clear()
                elif command_added == 0:
                    can_process = 0
                    parsing = 0
                else:
                    reply_message = command_list_original[0] + ' ' + command_list_original[1] + ' ' + command_list_original[2] 
                    can_process = 1
                    parsing = 0
            elif any(ext in command_list[0] for ext in constant.TIME_UNITS):
                time_to_add = 0
                unit_to_add = ""
                for unit in constant.TIME_UNITS:
                    if unit in command_list[0]:
                        time_to_add = command_list[0].replace(unit,'')
                        unit_to_add = unit
                if time_to_add.isdigit():
                    if command_added == 0:
                        message_time = datetime.now()
                        message_time = await add_time(message_time,time_to_add,unit_to_add)
                    else:
                        message_time = await add_time(message_time,time_to_add,unit_to_add)
                    command_added = 1
                    command = command_list_original[1]
                    command_list.clear()
                    command_list_original.clear()
                elif command_added == 0:
                    can_process = 0
                    parsing = 0
                else:
                    reply_message = command_list_original[0] + ' ' + command_list_original[1]
                    can_process = 1
                    parsing = 0

            elif any(ext in command_list[0] for ext in constant.AM_PM_LIST):

                for ending in constant.AM_PM_LIST:
                    if ending in command_list[0]:
                        am_pm = ending

                time_to_add = command_list[0].split(am_pm)[0]
                if time_to_add.isdigit():
                    time_to_add = int(time_to_add)
                    if am_pm == 'am':
                        time_to_add = time_to_add
                    else:
                        if time_to_add == 12:
                            time_to_add = 12
                        else:
                            time_to_add = time_to_add + 12
                    if time_to_add > 24:
                        can_process = 0
                        parsing = 0
                    else:
                        if command_added == 0:
                            message_time = datetime.now() + timedelta(hours=time_to_add)
                            command_added = 1
                        else:
                            message_time = message_time.replace(hour=time_to_add)
                        command = command_list_original[1]
                        command_list.clear()
                        command_list_original.clear()
                elif full_time_regex.match(time_to_add):
                    new_hour = time_to_add.split(':')[0]
                    new_minute = time_to_add.split(':')[1]
                    if new_hour.isdigit() and new_minute.isdigit():
                        new_hour = int(new_hour)
                        new_minute = int(new_minute)
                        if am_pm == 'am':
                            new_hour = new_hour
                        else:
                            if new_hour == 12:
                                new_hour = new_hour
                            else:
                                new_hour = new_hour + 12
                        if new_hour > 24:
                            can_process = 0
                            parsing = 0
                        else:
                            if command_added == 0:
                                message_time = datetime.now()
                                message_time = message_time.replace(hour=new_hour)
                                message_time = message_time.replace(minute=new_minute)
                                command_added = 1
                            else:
                                message_time = message_time.replace(hour=new_hour)
                                message_time = message_time.replace(minute=new_minute)

                            command = command_list_original[1]
                            command_list.clear()
                            command_list_original.clear()
                    else:
                        can_process = 0
                        parsing = 0
                else:
                    can_process = 0
                    parsing = 0

            elif number_date_regex.match(command_list[0]):
                if command_added == 0:
                    # Slash Date No Message
                    message_time = parser.parse(command_list[0])

                    # Add 9am time
                    message_time = message_time + timedelta(hours=9)
                    command = command_list_original[1]
                    command_list.clear()
                    command_list_original.clear()
                    command_added = 1
                else:
                    can_process = 1
                    parsing = 0
            else: 
                if command_added == 0:
                    can_process = 0
                    parsing = 0
                else:
                    reply_message = command_list_original[0] + ' ' + command_list_original[1]
                    can_process = 1
                    parsing = 0

        # Have more commmands to process
        elif len(command_list) == 3:

            # check time addition format
            if command_list[0].isdigit() and command_list[1] in constant.TIME_UNITS:
                if command_added == 0:
                    message_time = datetime.now()
                    message_time = await add_time(message_time,command_list[0],command_list[1])
                    command_added = 1
                else:
                    message_time = await add_time(message_time,command_list[0],command_list[1])
                command_added = 1
                command = command_list_original[2]
                command_list.clear()
                command_list_original.clear()

            elif any(ext in command_list[0] for ext in constant.AM_PM_LIST):

                for ending in constant.AM_PM_LIST:
                    if ending in command_list[0]:
                        am_pm = ending

                time_to_add = command_list[0].split(am_pm)[0]
                if time_to_add.isdigit():
                    time_to_add = int(time_to_add)
                    if am_pm == 'am':
                        time_to_add = time_to_add
                    else:
                        if time_to_add == 12:
                            time_to_add = 12
                        else:
                            time_to_add = time_to_add + 12
                    if time_to_add > 24:
                        can_process = 0
                        parsing = 0
                    else:
                        if command_added == 0:
                            message_time = datetime.now() + timedelta(hours=time_to_add)
                            
                            command_added = 1
                        else:
                            message_time = message_time.replace(hour=time_to_add)
                        command = command_list_original[1] + " " + command_list_original[2]
                        command_list.clear()
                        command_list_original.clear()
                        command_added = 1
                elif full_time_regex.match(time_to_add):
                    new_hour = time_to_add.split(':')[0]
                    new_minute = time_to_add.split(':')[1]
                    if new_hour.isdigit() and new_minute.isdigit():
                        new_hour = int(new_hour)
                        new_minute = int(new_minute)
                        if am_pm == 'am':
                            new_hour = new_hour
                        else:
                            if new_hour == 12:
                                new_hour = new_hour
                            else:
                                new_hour = new_hour + 12
                        if new_hour > 24:
                            can_process = 0
                            parsing = 0
                        else:
                            if command_added == 0:
                                message_time = datetime.now()
                                message_time = message_time.replace(hour=new_hour)
                                message_time = message_time.replace(minute=new_minute)
                                command_added = 1
                            else:
                                message_time = message_time.replace(hour=new_hour)
                                message_time = message_time.replace(minute=new_minute)

                            command = command_list_original[1] + " " + command_list_original[2]
                            command_list.clear()
                            command_list_original.clear()
                    else:
                        can_process = 0
                        parsing = 0
                else:
                    can_process = 0
                    parsing = 0

            elif any(ext in command_list[0] for ext in constant.TIME_UNITS):
                time_to_add = 0
                unit_to_add = ""
                for unit in constant.TIME_UNITS:
                    if unit in command_list[0]:
                        time_to_add = command_list[0].replace(unit,'')
                        unit_to_add = unit
                if time_to_add.isdigit():
                    if command_added == 0:
                        message_time = datetime.now()
                        message_time = await add_time(message_time,time_to_add,unit_to_add)
                    else:
                        message_time = await add_time(message_time,time_to_add,unit_to_add)
                    command_added = 1
                    command = command_list_original[1] + " " + command_list_original[2]
                    command_list.clear()
                    command_list_original.clear()
                elif command_added == 0:
                    can_process = 0
                    parsing = 0
                else:
                    reply_message = command_list_original[0] + ' ' + command_list_original[1] + ' ' + command_list_original[2] 
                    can_process = 1
                    parsing = 0

            elif number_date_regex.match(command_list[0]):
                if command_added == 0:
                    # Slash Date No Message
                    message_time = parser.parse(command_list[0])

                    # Add 9am time
                    message_time = message_time + timedelta(hours=9)
                    command = command_list_original[1] + " " + command_list_original[2]
                    command_list.clear()
                    command_list_original.clear()
                    command_added = 1
                else:
                    can_process = 1
                    parsing = 0
            elif command_list[0] in constant.MONTH_LIST:
                # Month being added
                message_time = await add_time_to_date(message_time,command_list[0],'month')
                command_added = 1
                command = command_list_original[1] + " " + command_list_original[2]
                command_list.clear()
                command_list_original.clear()

            elif command_list[0].isdigit():
                message_time = await add_time_to_date(message_time,command_list[0],'day')
                command_added = 1
                command = command_list_original[1] + " " + command_list[2]
                command_list.clear()
                command_list_original.clear()

            elif any(ext in command_list[0] for ext in constant.DAY_ENDINGS):
                date = ''
                for day_ending in constant.DAY_ENDINGS:
                    if day_ending in command_list[0]:
                        date = command_list[0].replace(day_ending,'')
                if date.isdigit():
                    message_time = await add_time_to_date(message_time,date,'day')
                    command_added = 1
                    command = command_list_original[1] + " " + command_list_original[2]
                    command_list.clear()
                    command_list_original.clear()
                elif command_added == 0:
                    can_process = 0
                    parsing = 0
                else:
                    reply_message = command_list_original[0] + ' ' + command_list_original[1] + ' ' + command_list_original[2] 
                    can_process = 1
                    parsing = 0
            else: 
                if command_added == 0:
                    can_process = 0
                    parsing = 0
                else:
                    reply_message = command_list_original[0] + ' ' + command_list_original[1] + ' ' + command_list_original[2] 
                    can_process = 1
                    parsing = 0

    if can_process == 1:
        now = datetime.now()
        if now < message_time:
            
            max_index = 0
            for timer in RemindMe_Timers:
                if max_index < int(timer.index):
                    max_index = int(timer.index)
            new_index = max_index + 1
            
            message_id = message.id
            message_channel_id = message.channel.id
            new_timer = RemindMe_Timer(new_index,message_time,message,message_id,message_channel_id,reply_message)
            RemindMe_Timers.append(new_timer)
            write_timer_to_file(new_timer)
            
        else:
            await message.channel.send("Can't go back in time")
    elif command_no_timer != 1:
        await message.channel.send("Invalid Command")

async def add_time(message_time,time_to_add_input,unit):

    new_message_time = message_time
    time_to_add = int(time_to_add_input)
    if unit in constant.SECONDS_UNITS:
        new_message_time = new_message_time + timedelta(seconds=time_to_add)
    elif unit in constant.MINUTES_UNITS:
        new_message_time = new_message_time + timedelta(minutes=time_to_add)
    elif unit in constant.HOURS_UNITS:
        new_message_time = new_message_time + timedelta(hours=time_to_add)
    elif unit in constant.DAYS_UNITS:
        new_message_time = new_message_time + timedelta(days=time_to_add)
    elif unit in constant.WEEKS_UNITS:
        new_message_time = new_message_time + timedelta(weeks=time_to_add)
    elif unit in constant.FORTNITES_UNITS:
        new_message_time = new_message_time + timedelta(weeks=time_to_add*2)
    elif unit in constant.MONTHS_UNITS:
        new_message_time = new_message_time.replace(month=new_message_time.month + time_to_add)
    elif unit in constant.YEARS_UNITS:
        new_message_time = new_message_time.replace(year=new_message_time.year + time_to_add)

    return new_message_time

async def add_time_to_date(message_time,command,day_month_year):

    if message_time == "":
        new_message_time = datetime.now().replace(hour=9,minute=0,second=0,microsecond=0)
    else:
        new_message_time = message_time

    if day_month_year == "day":
        new_message_time = new_message_time.replace(day=int(command))

    elif day_month_year == 'month':
        int_month = await convert_month_to_int(command)
        new_message_time = new_message_time.replace(month=int_month)
        current_month = datetime.now().month
        if current_month > int_month:
            new_message_time = new_message_time.replace(year=new_message_time.year + 1)

    elif day_month_year == 'year':
        int_year = int(command)

        if len(str(int_year)) == 2:
            int_year = int_year + 2000
        new_message_time = new_message_time.replace(year=int_year)

    return new_message_time

async def convert_month_to_int(month):
    if month == 'jan' or month == 'january':
        month_return = 1
    elif month == 'feb' or month == 'february':
        month_return = 2
    elif month == 'mar' or month == 'march':
        month_return = 3
    elif month == 'apr' or month == 'april':
        month_return = 4
    elif month == 'may':
        month_return = 5
    elif month == 'jun' or month == 'june':
        month_return = 6
    elif month == 'jul' or month == 'july':
        month_return = 7
    elif month == 'aug' or month == 'august':
        month_return = 8
    elif month == 'sept' or month == 'september':
        month_return = 9
    elif month == 'oct' or month == 'october':
        month_return = 10
    elif month == 'nov' or month == 'november':
        month_return = 11
    elif month == 'dec' or month == 'december':
        month_return = 12

    return month_return


async def start_remindme_timer(message,wait_time,unit,reply_message):

    if unit in constant.SECONDS_UNITS:
        message_time = datetime.now() + timedelta(seconds=wait_time)
    elif unit in constant.MINUTES_UNITS:
        message_time = datetime.now() + timedelta(minutes=wait_time)
    elif unit in constant.HOURS_UNITS:
        message_time = datetime.now() + timedelta(hours=wait_time)
    elif unit in constant.DAYS_UNITS:
        message_time = datetime.now() + timedelta(days=wait_time)
    elif unit in constant.WEEKS_UNITS:
        message_time = datetime.now() + timedelta(weeks=wait_time)
    elif unit in constant.FORTNITES_UNITS:
        message_time = datetime.now() + timedelta(weeks=wait_time*2)
    elif unit in constant.MONTHS_UNITS:
        message_time = datetime.now() + timedelta(months=wait_time)
    elif unit in constant.YEARS_UNITS:
        message_time = datetime.now() + timedelta(years=wait_time)

    max_index = 0
    for timer in RemindMe_Timers:
        if max_index < timer.index:
            max_index = timer.index
    new_index = max_index + 1

    message_id = message.id
    message_channel_id = message.channel.id
    if reply_message == "":
        reply_message = "<@" + str(message.author.id) + ">"

    new_timer = RemindMe_Timer(new_index,message_time,message,message_id,message_channel_id,reply_message)
    RemindMe_Timers.append(new_timer)
    write_timer_to_file(new_timer)

async def roll_dice(message,folder_name,dice_max_size,num_of_dice):
    
    if dice_max_size == 100:
        dice_roll = random.randrange(1,dice_max_size + 1)
        dice_roll_tens = dice_roll // 10
        dice_roll_single = dice_roll % 10
        if dice_roll_tens == 10:
            dice_roll_tens = 0
        image_file_name_tens = folder_name + str(dice_roll_tens) + "0.png"
        image_file_name_single = folder_name + str(dice_roll_single) + ".png"
        image_1 = Image.open(image_file_name_tens)
        image_2 = Image.open(image_file_name_single)
        image_combined = Image.new('RGBA', (image_1.width + image_2.width, image_1.height))
        image_combined.paste(image_1, (0, 0))
        image_combined.paste(image_2, (image_1.width, 0))
        image_combined.save(constant.TEMP_FILE_PATH)
        await message.channel.send(file=discord.File(constant.TEMP_FILE_PATH))
        os.remove(constant.TEMP_FILE_PATH)

    elif num_of_dice > 1:
        images = []
        width = 0
        height = 0
        for x in range(num_of_dice):
            dice_roll = random.randrange(1,dice_max_size + 1)
            image_file_name = image_file_name = folder_name + str(dice_roll) + ".png"
            image = Image.open(image_file_name)
            width = width + image.width
            if height == 0:
                height = image.height
            images.append(image)

        image_combined = Image.new('RGBA', (width, height))
        width = 0
        for image in images:
            image_combined.paste(image,(width,0))
            width = width + image.width

        image_combined.save(constant.TEMP_FILE_PATH)
        await message.channel.send(file=discord.File(constant.TEMP_FILE_PATH))
        os.remove(constant.TEMP_FILE_PATH)

    else:
        dice_roll = random.randrange(1,dice_max_size  + 1)
        if dice_max_size == 2:
            if dice_roll == 1:
                image_file_name = folder_name + "heads.png"
            else:
                image_file_name = folder_name + "tails.png"
        else:
            image_file_name = folder_name + str(dice_roll) + ".png"
        await message.channel.send(file=discord.File(image_file_name))

async def all_dice(message):

    images = []
    width = 0
    height = 0
    # All Special Dice
    for dice in constant.DICE_NUMBER_LIST:
        dice_roll = random.randrange(1,dice + 1)
        dice_folder_name = "pictures/d" + str(dice) + "/"
        if dice == 100:
            dice_roll_tens = dice_roll // 10
            dice_roll_single = dice_roll % 10
            if dice_roll_tens == 10:
                dice_roll_tens = 0
            image_file_name_tens = dice_folder_name + str(dice_roll_tens) + "0.png"
            image_file_name_single = dice_folder_name + str(dice_roll_single) + ".png"
            image_1 = Image.open(image_file_name_tens)
            image_2 = Image.open(image_file_name_single)
            width = width + image_1.width
            width = width + image_2.width
            images.append(image_1)
            images.append(image_2)
        else:
            image_file_name = image_file_name = dice_folder_name + str(dice_roll) + ".png"
            image = Image.open(image_file_name)
            width = width + image.width
            if height == 0:
                height = image.height
            images.append(image)

    # 2 Regular Dice
    for x in range(2):
        if x == 1:
            dice_folder_name = constant.BLACK_DICE_FOLDER_PATH
        else:
            dice_folder_name = constant.WHITE_DICE_FOLDER_PATH
        dice_roll = random.randrange(1,constant.REG_DICE_MAX + 1)
        image_file_name = image_file_name = dice_folder_name + str(dice_roll) + ".png"
        image = Image.open(image_file_name)
        width = width + image.width
        if height == 0:
            height = image.height
        images.append(image)

    # Coin
    dice_roll = random.randrange(1,constant.COIN_MAX + 1)
    dice_folder_name = constant.COIN_FOLDER_PATH
    if dice_roll == 1:
        image_file_name = dice_folder_name + "heads.png"
    else:
        image_file_name = dice_folder_name + "tails.png"

    image = Image.open(image_file_name)
    width = width + image.width
    if height == 0:
        height = image.height
    images.append(image)

    image_combined = Image.new('RGBA', (width, height))
    width = 0
    for image in images:
        image_combined.paste(image,(width,0))
        width = width + image.width

    image_combined.save(constant.TEMP_FILE_PATH)
    await message.channel.send(file=discord.File(constant.TEMP_FILE_PATH))
    os.remove(constant.TEMP_FILE_PATH)

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')

client = discord.Client()

@client.event
async def on_ready():
    for guild in client.guilds:
        if guild.name == GUILD:
            break

    check_remindme.start()

    await read_timers_from_file()
    print(f'{client.user} is connected to Discord!')
    print(f'{guild.name}(id: {guild.id})')

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith("!"):
        user_message = message.content.replace("!","")
        user_message_lower = user_message.lower()
        # RemindMe Logic
        if user_message_lower.startswith("remindme"):
            await new_parse_remindme_message(message,user_message)
            
        user_command = user_message.split(' ')
        if user_command[0].isdigit() and int(user_command[0]) in constant.DICE_NUMBER_LIST:
            dice_size = int(user_command[0])
            if dice_size == 100:
                dice_folder_name = "pictures/d" + str(dice_size) + "/"
                num_rolls = 1
                await roll_dice(message,dice_folder_name,dice_size,num_rolls)
            else:
                dice_folder_name = "pictures/d" + str(dice_size) + "/"
                num_rolls = 1
                if len(user_command) > 1:
                    if user_command[1].isdigit():
                        num_rolls = int(user_command[1])
                if num_rolls < constant.MAX_NUMBER_ROLLS:  
                    await roll_dice(message,dice_folder_name,dice_size,num_rolls)
                else:
                    await message.channel.send(file=discord.File(constant.SAD_DICE_KING_FILE_PATH))
        elif user_command[0].isdigit():
            await message.channel.send(file=discord.File(constant.SAD_DICE_KING_FILE_PATH))
        else:
            dice_color = random.randrange(1,constant.NUM_OF_REG_DICE_VARIATIONS + 1)
            if dice_color == 1:
                dice_folder_name = constant.BLACK_DICE_FOLDER_PATH
            else:
                dice_folder_name = constant.WHITE_DICE_FOLDER_PATH

            if user_command[0].lower() in constant.DICE_COMMAND_LIST:
                num_rolls = 1
                if len(user_command) > 1:
                    if user_command[1].isdigit():
                        num_rolls = int(user_command[1])
                if num_rolls < constant.MAX_NUMBER_ROLLS:   
                    await roll_dice(message,dice_folder_name,constant.REG_DICE_MAX,num_rolls)
                else:
                    await message.channel.send(file=discord.File(constant.SAD_DICE_KING_FILE_PATH))
            elif user_command[0].lower() in constant.CRAPS_COMMAND_LIST:
                await roll_dice(message,dice_folder_name,constant.REG_DICE_MAX,constant.NUM_ROLLS_CRAPS)
            elif user_command[0].lower() in constant.CEELO_COMMAND_LIST:
                await roll_dice(message,dice_folder_name,constant.REG_DICE_MAX,constant.NUM_ROLLS_CEELO)
            elif user_command[0].lower() in constant.COIN_COMMAND_LIST:
                num_rolls = 1
                if len(user_command) > 1:
                    if user_command[1].isdigit():
                        num_rolls = int(user_command[1])
                if num_rolls < constant.MAX_NUMBER_ROLLS:   
                    await roll_dice(message,constant.COIN_FOLDER_PATH,constant.COIN_MAX,num_rolls)
                else:
                    await message.channel.send(file=discord.File(constant.SAD_DICE_KING_FILE_PATH))
            elif user_command[0].lower() in constant.ALL_COMMAND_LIST:
                await all_dice(message)
            elif user_command[0].lower() in constant.HELP_COMMAND_LIST:
                await message.channel.send(constant.HELP_ME_STRING)

@tasks.loop(seconds=1)
async def check_remindme():
    for remind_me in RemindMe_Timers:
        if remind_me.time < datetime.now():
            await remind_me.message.channel.send(remind_me.reply_message, reference=remind_me.message)
            remove_timer_to_file(remind_me)
            RemindMe_Timers.remove(remind_me)

client.run(TOKEN)