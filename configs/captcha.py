captcha_list = ['Яблоко','Банан','Арбуз','Морковь','Виноград','Кукурузу']
captcha_smiles_list = ['🍎','🍌','🍉','🥕','🍇','🌽']
callbacks_for_smiles = ['cap1','cap2','cap3','cap4','cap5','cap6']
#dictionaries
captcha_callbacks = dict(zip(captcha_list,callbacks_for_smiles))
captcha_smiles = dict(zip(captcha_list,captcha_smiles_list))
smiles_callbacks = dict(zip(captcha_smiles_list,callbacks_for_smiles))