from configs.captcha import captcha_list,captcha_smiles,captcha_callbacks
from random import randint

def selectRandomFruit():
    food = captcha_list[randint(0,5)]
    smile = captcha_smiles.get(food)
    callback = captcha_callbacks.get(food)
    return [food,smile,callback]