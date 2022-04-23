# main.py
import os
import random
from PIL import Image
from os.path import exists

import discord
from dotenv import load_dotenv

dice_number_list = [4,6,8,10,12,20,100]
dice_command_list = ["dice","craps","cee-lo","ceelo"]
reg_dice_max = 6
num_of_reg_dice_variations = 2
num_rolls_craps = 2
num_rolls_ceelo = 3
max_number_rolls = 21

sad_dice_king_file_path = 'pictures/dice_king/sad_dice_king.png'
temp_file_path = 'pictures/temp/combined.png'

help_me_string = "I'm King Dice, proprietor of this server. Your one and only stop for all dice-related needs. Here is how to use me, and good luck friend!\n\n!dice – roll a regular 6-sided die \n!craps – rolls 2 6-sided die\n!ceelo – rolls 3 6-sided die\n!20 – rolls a d20 die, also works for 12/10/8/6/4\n!100 – rolls 2d10, one for the first digit and one for the second (000 is 100)\n\nAnd don’t even think about doing a number after the exclamation mark that isn’t listed above this.. "

async def roll_dice(message,folder_name,dice_max_size,num_of_dice):
    if dice_max_size == 100:
        dice_roll = random.randrange(1,dice_max_size + 1)
        dice_roll_tens = dice_roll // 10
        dice_roll_single = dice_roll % 10
        image_file_name_tens = folder_name + str(dice_roll_tens) + "0.png"
        image_file_name_single = folder_name + str(dice_roll_single) + ".png"
        image_1 = Image.open(image_file_name_tens)
        image_2 = Image.open(image_file_name_single)
        image_combined = Image.new('RGBA', (image_1.width + image_2.width, image_1.height))
        image_combined.paste(image_1, (0, 0))
        image_combined.paste(image_2, (image_1.width, 0))
        image_combined.save(temp_file_path)
        await message.channel.send(file=discord.File(temp_file_path))
        os.remove(temp_file_path)

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

        image_combined.save(temp_file_path)
        await message.channel.send(file=discord.File(temp_file_path))
        os.remove(temp_file_path)

    else:
        dice_roll = random.randrange(1,dice_max_size  + 1)
        image_file_name = folder_name + str(dice_roll) + ".png"
        await message.channel.send(file=discord.File(image_file_name))

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')

client = discord.Client()

@client.event
async def on_ready():
    for guild in client.guilds:
        if guild.name == GUILD:
            break

    print(f'{client.user} is connected to Discord!')
    print(f'{guild.name}(id: {guild.id})')

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith("!"):
        user_message = message.content.replace("!","")
        user_command = user_message.split(' ')
        if user_command[0].isdigit() and int(user_command[0]) in dice_number_list:
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
                if num_rolls < max_number_rolls:  
                    await roll_dice(message,dice_folder_name,dice_size,num_rolls)
                else:
                    await message.channel.send(file=discord.File(sad_dice_king_file_path))
        elif user_command[0].isdigit():
            await message.channel.send(file=discord.File(sad_dice_king_file_path))
        else:
            dice_color = random.randrange(1,num_of_reg_dice_variations + 1)
            if dice_color == 1:
                dice_folder_name = "pictures/black_dice/"
            else:
                dice_folder_name = "pictures/white_dice/"

            if user_command[0].lower() == "dice":
                num_rolls = 1
                if len(user_command) > 1:
                    if user_command[1].isdigit():
                        num_rolls = int(user_command[1])
                if num_rolls < max_number_rolls:   
                    await roll_dice(message,dice_folder_name,reg_dice_max,num_rolls)
                else:
                    await message.channel.send(file=discord.File(sad_dice_king_file_path))
            elif user_command[0].lower() == "craps":
                await roll_dice(message,dice_folder_name,reg_dice_max,num_rolls_craps)
            elif user_command[0].lower() == "cee-lo" or user_command[0] == "ceelo":
                await roll_dice(message,dice_folder_name,reg_dice_max,num_rolls_ceelo)
            elif user_command[0].lower() == "dicehelp":
                await message.channel.send(help_me_string)
client.run(TOKEN)