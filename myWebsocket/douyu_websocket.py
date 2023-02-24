import asyncio
import os
import re
import time

# from playsound import playsound
import simpleaudio as sa
from aiowebsocket.converses import Converse

import settings
import json

from myLogger.log import logger


class DouyuWebSocket:
    def __init__(self):
        self.room_id = settings.ROOM_ID

    async def login_msg(self):
        """
        发送登录请求消息
        """
        msg = f"type@=loginreq/roomid@={self.room_id}/"
        msg_bytes = await self.dy_encode(msg)
        return msg_bytes

    async def group_msg(self):
        """发送入组消息"""
        msg = f"type@=joingroup/rid@={self.room_id}/gid@=-9999/"
        msg_bytes = await self.dy_encode(msg)
        return msg_bytes

    async def keeplive(self, converse: Converse) -> None:
        while True:
            """
            保持心跳
            """
            msg = f"type@=keeplive/tick@={str(int(time.time()))}/\0"
            beat_msg = await self.dy_encode(msg)
            await converse.send(beat_msg)
            await asyncio.sleep(15)

    async def on_message(self, message: bytes) -> dict:
        """
        将字节流转化为字符串，忽略无法解码的错误（即斗鱼协议中的头部尾部）
        """
        f = open('data.json', "rb")
        testF = open('log.txt', "a+",encoding='UTF-8')
        data = json.load(f)
        originalmMsg = message.decode(encoding="utf-8", errors="ignore")
        msgCount = originalmMsg.count("type")
        count = 1
        newMsg = []
        index = 0
        nextIndex = originalmMsg.find("type")
        index = nextIndex
        while count < msgCount:
            nextIndex = originalmMsg.index("type", index + 4)
            newMsg.append(originalmMsg[index:nextIndex])
            index = nextIndex
            count = count + 1
        newMsg.append(originalmMsg[index:])
        for msg in newMsg:
            testF.writelines(msg + "\n")
            if re.search(r"type@=(.*?)/", msg):
                msg_type = re.search(r"type@=(.*?)/", msg).group(1)
                # if msg_type == "chatmsg":
                #     barrage_dict = await self.format_barrage_dict(msg)
                #     return barrage_dict
                if msg_type == "dgb":
                    if int(re.search(r"gfid@=(.+?)/", msg).group(1)) == 824:
                        return {}
                    barrage_dict = await self.format_gift_dict(msg)
                    # print(msg)
                    # print(str(re.search(r"gfcnt@=(.+?)/", msg).group(1)) + "个 ")
                    for i in data:
                        if i['id'] == int(re.search(r"gfid@=(.+?)/", msg).group(1)) and int(i['pc']) > 0:
                            print(str(re.search(r"gfcnt@=(.+?)/", msg).group(1)) + "个 " + i['name'])
                            price = int(i['pc']) * int(re.search(r"gfcnt@=(.+?)/", msg).group(1))
                            # print(price)
                            if price >= 50000:
                                mystring = "audio-1.wav"
                                print("play audio 1")
                            elif price >= 20000:
                                mystring = "audio-2.wav"
                                print("play audio 2")
                            elif price >= 10000:
                                mystring = "audio-3.wav"
                                print("play audio 3")
                            # playsound(mystring)
                            try:
                                wave_obj = sa.WaveObject.from_wave_file(mystring)
                                play_obj = wave_obj.play()
                                play_obj.wait_done()
                            except:  # noqa
                                print(str(re.search(r"gfcnt@=(.+?)/", msg).group(1)) + "个 " + i['name'])
                            break
                    return barrage_dict
                elif msg_type == "rndfbc":
                    print("钻粉" + str(re.search(r"mn@=(.+?)/", msg).group(1)) + "个月")
                    price = 178 * int(re.search(r"mn@=(.+?)/", msg).group(1)) * 100
                    if price >= 50000:
                        mystring = "audio-1.wav"
                        print("play audio 1")
                    elif price >= 20000:
                        mystring = "audio-2.wav"
                        print("play audio 2")
                    elif price >= 10000:
                        mystring = "audio-3.wav"
                        print("play audio 3")
                    # playsound(mystring)
                    try:
                        wave_obj = sa.WaveObject.from_wave_file(mystring)
                        play_obj = wave_obj.play()
                        play_obj.wait_done()
                    except:  # noqa
                        print("err")
                    break
                    return {}
            elif re.search(r"@AA", msg):
                return {}
            else:
                logger.error(f"奇怪的msg:{msg}")

    @classmethod
    async def dy_encode(cls, msg: str) -> bytes:
        """
        编码
        """
        # 头部8字节，尾部1字节，与字符串长度相加即数据长度
        data_len = len(msg) + 9
        # 字符串转化为字节流
        msg_byte = msg.encode("utf-8")
        # 将数据长度转化为小端整数字节流
        len_byte = int.to_bytes(data_len, 4, "little")
        # 前两个字节按照小端顺序拼接为0x02b1，转化为十进制即689（《协议》中规定的客户端发送消息类型）
        # 后两个字节即《协议》中规定的加密字段与保留字段，置0
        send_byte = bytearray([0xb1, 0x02, 0x00, 0x00])
        # 尾部以"\0"结束
        end_byte = bytearray([0x00])
        # 按顺序拼接在一起
        data = len_byte + len_byte + send_byte + msg_byte + end_byte
        return data

    @classmethod
    async def format_barrage_dict(cls, msg: str) -> dict:
        try:
            barrage_dict = dict(
                rid=int(re.search(r"rid@=(.*?)/", msg).group(1)),  # 房间号
                uid=int(re.search(r"uid@=(.*?)/", msg).group(1)),  # 用户id
                nickname=re.search(r"nn@=(.*?)/", msg).group(1),  # 用户昵称
                level=int(re.search(r"level@=(.*?)/", msg).group(1)),  # 用户等级
                bnn=re.search(r"bnn@=(.*?)/", msg).group(1),  # 粉丝牌名称
                bnn_level=int(re.search(r"bl@=(.*?)/", msg).group(1)),  # 粉丝牌等级
                brid=int(re.search(r"brid@=(.*?)/", msg).group(1)),  # 粉丝牌房间号
                is_diaf=int(re.search(r"diaf@=(.*?)/", msg).group(1)) if "diaf@=" in msg else 0,  # 是否是钻石粉丝
                content=re.search(r"txt@=(.*?)/", msg).group(1)  # 弹幕内容
            )
            return barrage_dict
        except:  # noqa
            logger.error(f"奇怪的msg:{msg}")
            return {}

    @classmethod
    async def format_gift_dict(cls, msg: str) -> dict:
        try:
            barrage_dict = dict(
                rid=int(re.search(r"rid@=(.*?)/", msg).group(1)),  # 房间号
                uid=int(re.search(r"uid@=(.*?)/", msg).group(1)),  # 用户id
                nickname=re.search(r"nn@=(.*?)/", msg).group(1),  # 用户昵称
                level=int(re.search(r"level@=(.*?)/", msg).group(1)),  # 用户等级
                bnn=re.search(r"bnn@=(.*?)/", msg).group(1),  # 粉丝牌名称
                bnn_level=int(re.search(r"bl@=(.*?)/", msg).group(1)),  # 粉丝牌等级
                brid=int(re.search(r"brid@=(.*?)/", msg).group(1)),  # 粉丝牌房间号
                is_diaf=int(re.search(r"diaf@=(.*?)/", msg).group(1)) if "diaf@=" in msg else 0,  # 是否是钻石粉丝
                # content=re.search(r"txt@=(.*?)/", msg).group(1),  # 弹幕内容
                content=re.search(r"gfid@=(.+?)/", msg).group(1),
                num=re.search(r"gfcnt@=(.+?)/", msg).group(1)
            )
            return barrage_dict
        except:  # noqa
            logger.error(f"奇怪的msg:{msg}")
            return {}
