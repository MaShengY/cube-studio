import base64
import io,sys,os
from cubestudio.aihub.model import Model,Validator,Field_type,Field

import pysnooper
import os

class MGEO_GEOGRAPHIC_ENTITY_ALIGNMENT_CHINESE_BASE_Model(Model):
    # 模型基础信息定义
    name='mgeo-geographic-entity-alignment-chinese-base'   # 该名称与目录名必须一样，小写
    label='MGeo地址相似度匹配实体对齐-中文-地址领域-base'
    describe="模型判断两条地址是否指代同一道路、村庄、POI等。将两条地址的关系分为完全对齐、部分对齐、不对齐。该任务是构建地理信息知识库的核心技术。"
    field="自然语言"    # [机器视觉，听觉，自然语言，多模态，强化学习，图论]
    scenes=""
    status='online'
    version='v20221001'
    pic='example.jpg'  # 离线图片，作为模型的样式图，330*180尺寸比例
    hot = "40402"
    frameworks = "pytorch"
    doc = "https://modelscope.cn/models/damo/mgeo_geographic_entity_alignment_chinese_base/summary"

    # 和train函数的输入参数对应，并且会对接显示到pipeline的模板参数中
    train_inputs = []

    # 和inference函数的输入参数对应，并且会对接显示到web界面上
    inference_inputs = [
        Field(type=Field_type.text, name='arg0', label='',describe='',default='',validators=Validator(max=100)),
        Field(type=Field_type.text, name='arg1', label='',describe='',default='',validators=Validator(max=100))
    ]

    inference_resource = {
        "resource_gpu": "0"
    }
    # 会显示在web界面上，让用户作为示例输入
    web_examples=[
        {
            "label": "示例0",
            "input": {
                "arg0": "紫萱路363号人力社保局",
                "arg1": "紫萱路363号市人社局"
            }
        },
        {
            "label": "示例1",
            "input": {
                "arg0": "紫萱路363号人力社保局",
                "arg1": "紫萱路市人社局"
            }
        },
        {
            "label": "示例2",
            "input": {
                "arg0": "紫萱路363号人力社保局",
                "arg1": "榆林市榆阳区康安路榆林市第二医院"
            }
        },
        {
            "label": "示例3",
            "input": {
                "arg0": "栖霞区仙林街道文枢东路2号商住楼4楼",
                "arg1": "栖霞区文枢东路2号书店"
            }
        }
    ]

    # 训练的入口函数，此函数会自动对接pipeline，将用户在web界面填写的参数传递给该方法
    def train(self,save_model_dir,arg1,arg2, **kwargs):
        pass
        # 训练的逻辑
        # 将模型保存到save_model_dir 指定的目录下


    # 加载模型，所有一次性的初始化工作可以放到该方法下。注意save_model_dir必须和训练函数导出的模型结构对应
    def load_model(self,save_model_dir=None,**kwargs):
        from modelscope.pipelines import pipeline
        from modelscope.utils.constant import Tasks
        
        self.p = pipeline('sentence-similarity', 'damo/mgeo_geographic_entity_alignment_chinese_base')

    # rtsp流的推理,输入为cv2 img,输出也为处理后的cv2 img
    def rtsp_inference(self,img:numpy.ndarray,**kwargs)->numpy.ndarray:
        return img

    # web每次用户请求推理，用于对接web界面请求
    @pysnooper.snoop(watch_explode=('result'))
    def inference(self,arg0,arg1,**kwargs):
        result = self.p({"arg0": arg0, "arg1": arg1})

        # 将结果保存到result目录下面，gitignore统一进行的忽略。并且在结果中注意添加随机数，避免多人访问时，结果混乱
        # 推理的返回结果只支持image，text，video，audio，html，markdown几种类型
        back=[
            {
                "image": 'result/aa.jpg',
                "text": '结果文本',
                "video": 'result/aa.mp4',
                "audio": 'result/aa.mp3',
                "markdown":''
            }
        ]
        return back

model=MGEO_GEOGRAPHIC_ENTITY_ALIGNMENT_CHINESE_BASE_Model()


# 容器中调试训练时
# save_model_dir = "result"
# model.train(save_model_dir = save_model_dir,arg1=None,arg2=None)  # 测试

# 容器中运行调试推理时
model.load_model(save_model_dir=None)
result = model.inference(arg0='紫萱路363号人力社保局',arg1='紫萱路363号市人社局')  # 测试
print(result)

# # 模型启动web时使用
# if __name__=='__main__':
#     model.run()