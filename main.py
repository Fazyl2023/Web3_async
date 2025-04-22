import asyncio
import random
from web3 import AsyncHTTPProvider, AsyncWeb3
from web3.eth import AsyncEth
from web3 import AsyncWeb3
import os
import asyncio
import aiofiles
import time
from aiohttp import ClientTimeout

# rpc ссылка https://arbitrum-one.public.blastapi.io

# Адрес прокси
Username = 'your proxy username'
passwd = 'your proxy password'
port = 'proxy port'
ip = 'your proxy ip address'

os.environ['HTTP_PROXY'] = f'http://{Username}:{passwd}@{ip}:{port}'

class Client:
    def __init__(self, rpc: str, private_key: str | None = None):
        self.rpc = rpc
        # Для того чтобы долго не ждал запрос
        timeout = ClientTimeout(total=10)
        self.provider = AsyncHTTPProvider(endpoint_uri=self.rpc, request_kwargs={"timeout": timeout})

        self.w3 = AsyncWeb3(
            provider = self.provider,
            modules={'eth': AsyncEth},
            middleware=[]
            )
        
        if private_key:            
            self.account = self.w3.eth.account.from_key(private_key = private_key)
        else:
            self.account = self.w3.eth.account.create(extra_entropy=str(random.randint(1, 999_999_999)))
        

    async def get_balance(self, address: str | None = None):
        if not address:
            await asyncio.sleep(0)
            address = self.account.address
        return await self.w3.eth.get_balance(account=address)
    # Функция для записи адреса, ключа и баланса в текстовый файл
    
    async def zapis(self):
        balance = await self.get_balance()
        async with aiofiles.open("site.txt", "a") as f:
            return await f.write(f'\naddress: {self.account.address} \n private key: {self.account.key.hex()} \n balance: {balance}')
    
    async def close(self):
         try:
             try:
                 await self.get_balance()
             except Exception:
                 pass  
             request_func = getattr(self.provider, '_request_func', None)  
             session = getattr(request_func, '_session', None)
             
             if session and not session.closed:
                 await session.close()
         except Exception as e:
                print(f'ошибка тут: {e}' )       

async def main():
        
    tasks = []
    clients = []
    
    # Засовываю в массив 1000 кошельков и балансы 
    for i in range(1, 1000):
               # С этим публичным rpc работает, но он медленный или перегруженный (по словам ChatGPT), поэтому много пропускает
               client = Client(rpc = 'https://arbitrum-one.public.blastapi.io')
               clients.append(client)
               #задача записи в файл автоматический вызывает задачу получения баланса
               tasks.append(client.zapis())
    
    # Создаю задачи         
    results1 = await asyncio.gather(
         *tasks, 
         return_exceptions= True)

    #Задача на закрытие текущей сессии(проблемы, не могу закрыть нормально)
    await asyncio.gather(*[client.close() for client in clients])
    for i, result in enumerate(results1):
         if isinstance(result, Exception):
              print(f'Ошибка в задаче {i}: {type(result).__name__} - {result}')  
    print(results1)

if __name__ == '__main__':
    asyncio.run(main())
    t2 = time.time()
    print(t2)
