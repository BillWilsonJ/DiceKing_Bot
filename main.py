# main.py
import os
import random
from PIL import Image
import constant

import discord
from dotenv import load_dotenv

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

            if user_command[0].lower() == "dice":
                num_rolls = 1
                if len(user_command) > 1:
                    if user_command[1].isdigit():
                        num_rolls = int(user_command[1])
                if num_rolls < constant.MAX_NUMBER_ROLLS:   
                    await roll_dice(message,dice_folder_name,constant.REG_DICE_MAX,num_rolls)
                else:
                    await message.channel.send(file=discord.File(constant.SAD_DICE_KING_FILE_PATH))
            elif user_command[0].lower() == "craps":
                await roll_dice(message,dice_folder_name,constant.REG_DICE_MAX,constant.NUM_ROLLS_CRAPS)
            elif user_command[0].lower() == "cee-lo" or user_command[0] == "ceelo":
                await roll_dice(message,dice_folder_name,constant.REG_DICE_MAX,constant.NUM_ROLLS_CEELO)
            elif user_command[0].lower() == "coin" or user_command[0] == "coinflip":
                num_rolls = 1
                if len(user_command) > 1:
                    if user_command[1].isdigit():
                        num_rolls = int(user_command[1])
                if num_rolls < constant.MAX_NUMBER_ROLLS:   
                    await roll_dice(message,constant.COIN_FOLDER_PATH,constant.COIN_MAX,num_rolls)
                else:
                    await message.channel.send(file=discord.File(constant.SAD_DICE_KING_FILE_PATH))
            elif user_command[0].lower() == "dicehelp":
                await message.channel.send(constant.HELP_ME_STRING)

client.run(TOKEN)