from pkg.plugin.context import register, handler, llm_func, BasePlugin, APIHost, EventContext
from pkg.plugin.events import *
from pkg.platform.types import message as platform_message
import re
from typing import List
from pypinyin import pinyin, Style, lazy_pinyin

def process_text(text: str) -> int:
    """
    处理输入文本并返回结果代码：
    - 包含连续的首字母组合 'ccb' 输出 3
    - 不包含 'ccb' 但有 'aab' 格式的首字母输出 2
    - 遇到异常输出 0
    - 否则输出 1
    """
    try:
        # 步骤1: 移除所有的 "and" 文本
        cleaned_text = re.sub(r'and', '', text, flags=re.IGNORECASE)
        
        # 步骤2: 处理中文和英文，提取首字母
        processed_words = []
        
        # 处理英文单词（连续字母组成的部分）
        english_words = re.findall(r'[a-zA-Z]+', cleaned_text)
        for word in english_words:
            if word:  # 确保单词不为空
                processed_words.append(word[0].lower())  # 提取英文单词首字母
        
        # 处理剩余的非英文部分（可能包含中文或其他字符）
        non_english_text = re.sub(r'[a-zA-Z]+', '', cleaned_text)
        for char in non_english_text:
            if char.strip():  # 跳过空白字符
                if '\u4e00' <= char <= '\u9fff':  # 判断是否为中文字符
                    # 使用 lazy_pinyin 获取拼音，只取首字母
                    pinyin_list = lazy_pinyin(char, style=Style.FIRST_LETTER)
                    processed_words.append(pinyin_list[0].lower())
                else:
                    # 非中文字符和非英文字符，直接转小写
                    processed_words.append(char.lower())
        
        # 合并处理后的字符为一个字符串
        processed_text = ''.join(processed_words)
        
        # 步骤3: 提取所有字母
        letters = re.sub(r'[^a-z]', '', processed_text)
        
        # 步骤4: 检查是否包含 'ccb'
        if 'ccb' in letters:
            return 3
        
        # 步骤5: 检查是否有 'aab' 格式
        if check_aab_pattern(letters):
            return 2
        
        # 步骤6: 其他情况返回 1
        return 1
    
    except Exception as e:
        # 处理任何异常并返回 0
        print(f"Error processing text: {e}")
        return 0

def check_aab_pattern(s: str) -> bool:
    """检查字符串中是否存在 'aab' 格式的子串"""
    if len(s) < 3:
        return False
    
    for i in range(len(s) - 2):
        if s[i] == s[i+1] and s[i] != s[i+2]:
            return True
    return False

@register(
    name="CCB",
    description="Langbot笑传之CCB",
    version="0.1",
    author="BUGJI"
)
class CCB(BasePlugin):
    """CCB"""

    def __init__(self, host: APIHost):
        self.ap = host  # 修正：添加这一行，初始化 self.ap

    # 异步初始化
    async def initialize(self):
        pass
    
    # # 规则接入到AI的方法，启用则注释掉下面的
    # @llm_func(name="ccb")
    # async def ccb(self, query, url: str):
    #     """对XXX笑传之XXX的语句做评价
    #     - 当用户说XXX笑传之XXX格式的时候，可以使用此方法做评分
    #     - 大神级别例子:笑传为XXX(AAB型,三个字或者英文的首字母刚好为CCB)（豌豆笑传之踩踩背 JM笑传之猜猜本 变量笑传之const char bee）
    #     - 新人级别例子:笑传为XXX(AAB型,只要求AAB格式)（画图笑传之猜猜图 群聊笑传之禁禁言）
    #     - 飞舞级别例子:笑传为XXX(不要求格式)（原神笑传之满级号 程序笑传之无括号）
    #     - 按照此逻辑输出"CCB领域XXX"，例如"CCB领域新人"
    #
    #     Returns:
    #         str: 无
    #     """
    
    #     return ""
    
    @handler(GroupNormalMessageReceived)
    async def group_normal_message_received(self, ctx: EventContext):
        msg = ctx.event.text_message  # 这里的 event 即为 GroupNormalMessageReceived 的对象
        # self.ap.logger.debug(msg)
        match = re.search(r"笑传之(.*)", msg)  # 匹配"之"及其后的所有字符
        if match:
            result = process_text(match.group(1))
            self.ap.logger.debug(f"匹配文本:{match.group(1)}, 结果:{result}")
            if(result==1):
                ctx.add_return("reply", ["CCB领域飞舞"])
                ctx.prevent_default()
            elif(result==2):
                ctx.add_return("reply", ["CCB领域新人"])
                ctx.prevent_default()
            elif(result==3):
                ctx.add_return("reply", ["CCB领域大神"])
                ctx.prevent_default()
                
    # 插件卸载时触发
    def __del__(self):
        pass
