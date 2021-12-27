import subprocess as sbp
import pip

pkgs = eval(str(sbp.run("pip3 list -o --format=json", shell=True,
                        stdout=sbp.PIPE).stdout, encoding='utf-8'))
for pkg in pkgs:
    sbp.run("pip3 install --upgrade " + pkg['name'], shell=True)

'''
adduser valstan
usermod -aG sudo valstan
reboot
su - valstan
sudo -S apt update
sudo apt upgrade
sudo dpkg-reconfigure locales
sudo apt install mc
sudo apt -y install python3-pip
sudo apt install nano
nano .bashrc
Добавляем в конец строку:
export PATH=/home/valstan/.local/bin:$PATH
(Выбрать строку установки PyTorch на сайте - https://pytorch.org/get-started/locally/#start-locally)
pip3 install torch==1.10.1+cpu torchvision==0.11.2+cpu torchaudio==0.10.1+cpu -f https://download.pytorch.org/whl/cpu/torch_stable.html
pip3 install easyocr
pip3 install --upgrade TensorFlow
pip3 install pymorphy2 pytz instabot pymongo dnspython vk_api
(SSL urllib3 shutil Pillow zipfile ненужно устанавливать или уже есть в питоне3 или установилоась с прошлыми прогами)
sudo apt install git
git config --global user.name "ubuntuvalstan"
git config --global user.email 123qwemmm@mail.ru
git config --global core.editor nano
Первый раз клонировать репу на сервер:
cd
git clone https://github.com/Valstan/postopus
Обновлять репу:
cd postopus
git pull https://github.com/Valstan/postopus
mkdir config
mkdir insta_photo
EDITOR=nano crontab -e
'''