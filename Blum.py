import requests as req
import msvcrt
import json
import os
import time
import random

class JWT:
    def __init__(self, filename: str) -> None:
        self._tokens = []
        self._filename = filename
        self._load()
    
    def _load(self):
        try:
            with open(self._filename) as f:
                self._tokens = json.load(f)
        except:
            print('File not found '+self._filename)
            self._tokens = []
    
    def _save(self):
        with open(self._filename, 'w') as f:
            f.write(json.dumps(self._tokens, sort_keys=True, indent=4))

    def add(self, name: str, token: str):
        self._tokens.append({
            "id": str(self.count() + 1),
            "name": name,
            "token": token
        })
        self._save()

    def check(self, jwtStr: str) -> str:
        for data in self._tokens:
            if data['id'] == jwtStr:
                jwtStr = data['token']
                print('Профиль '+data['id']+' ('+data['name']+')')
                break
        return jwtStr
    
    def print(self):
        print("Доступные профили(всего "+str(self.count())+")")
        for data in self._tokens:
            print(data['id']+' - '+data['name'])

    def update(self, id: int, token: str) -> tuple[bool, str]:
        for p in self._tokens:
            if p['id'] == str(id):
                p['token'] = token
                self._save()
                return True, p['name']
        return False, 'failed'
    
    def remove(self, id: int) -> tuple[bool, str]:
        removed, name = False, 'failed'
        for i in range(self.count()):
            if self._tokens[i]['id'] == str(id):
                removed = True
                name = self._tokens[i]['name']
                self._tokens.pop(i)
                break
        if removed:
            for i in range(id-1, self.count()):
                self._tokens[i]['id'] = str(int(self._tokens[i]['id']) - 1)
            self._save()
        return removed, name

    def count(self) -> int:
        return len(self._tokens)

def menu():
    print('\n======== BLUM ========')
    print('A - Add profile')
    print('P - Profiles')
    print('R - Remove profile')
    print('U - Update profile')
    print('S - Start farm')
    print('X - Exit')
    print('======================\n')
    print('>>> Нажмите нужную клавишу ')

def main(jwt: str):
    head = {
        'Authorization': 'Bearer' + jwt,
        'Accept': 'application/json',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0'
    }
    resp = req.get('https://game-domain.blum.codes/api/v1/user/balance', headers=head)
    data = json.loads(resp.text)
    #print('#balance data:', data)
    try:
        count = int(input('Введите количество игр(у вас доступно '+str(data['playPasses'])+'): '))
        assert count > 0, 'Количество должно быть больше нуля'
        assert count <= data['playPasses'], 'Количество должно быть меньше '+str(data['playPasses'])
    except KeyError:
        return print('Ошибка: '+data['message'],end='\n\n\n\n')
    except AssertionError as e:
        return print('Ошибка: '+str(e),end='\n\n\n\n')
    total_point = 0
    print("Начал играть...")
    for i in range(count):
        head = {
            'Authorization': 'Bearer' + jwt,
            'Accept': 'application/json',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0'
        }
        post_id = req.post('https://game-domain.blum.codes/api/v1/game/play', headers=head)
        data = json.loads(post_id.text)
        #print('#play data:', data)
        id = data['gameId']
        delay = random.randrange(30, 40, 2)
        print('Идет игра, ожидайте '+str(delay)+' секунд')
        time.sleep(delay)
        points = random.randint(260, 280)
        endGame = req.post('https://game-domain.blum.codes/api/v1/game/claim', headers=head, json={
            "gameId": id, "points": points})
        print(str(i + 1) + ' / ' + str(count) + " игр. За последнюю игру +"+str(points))
        total_point += points
        if i+1 < count:
            time.sleep(random.randint(1, 5))
        
    print("End. Всего зафармленно поинтов:", total_point)

if __name__ == '__main__':
    parser = JWT('Blum.json')
    while True:
        menu()
        key = msvcrt.getch()
        if key == b'x' or key == b'\xe7':
            exit()
        elif key == b'a' or key == b'\xe4':
            os.system('cls')
            name = input('>>> введите название профиля: ')
            token = input('>>> введите токен Bearer из блума: ')
            parser.add(name, token)
            print('\nдобавлен профиль: '+name)
        elif key == b's' or key == b'\xeb':
            os.system('cls')
            parser.print()
            jwt = input(">>> Введите Bearer из Блума или номер профиля: ")
            main(parser.check(jwt))
        elif key == b'p' or key == b'\xa7':
            os.system('cls')
            parser.print()
        elif key == b'u' or key == b'\xa3':
            os.system('cls')
            parser.print()
            try:
                id = int(input('>>> введите ид профиля для апдейта: '))
                assert id > 0
                assert id <= parser.count()
                updated, name = parser.update(id, input('>>> введите новый токен: '))
                if updated:
                    print('обновлен токен для '+name)
                else:
                    print('не удалось обновить')
            except:
                print('некорректный ид профиля')
        elif key == b'r' or key == b'\xaa':
            os.system('cls')
            parser.print()
            try:
                id = int(input('>>> введите ид профиля для удаления: '))
                assert id > 0
                assert id <= parser.count()
                removed, name = parser.remove(id)
                if removed:
                    print('удален успешно: '+name)
                else:
                    print('не удалось удалить')
            except:
                print('некорректный ид профиля')
        else:
            continue
        print('\n>>> Нажмите любую клавишу чтобы отобразить меню')
        msvcrt.getch()
        os.system('cls')
