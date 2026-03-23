import time
import requests
import json


def generate_image(api_key, model, prompt, size="1024*1024", n=1):
    """
    调用阿里云 DashScope API 生成图像 (支持 Qwen-Image-2.0 / Wanx)
    """
    url = "https://dashscope.aliyuncs.com/api/v1/services/aigc/text2image/image-synthesis"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "X-DashScope-Async": "enable"
    }
    
    # 适配模型参数
    # wanx-v1, wanx-v2, qwen-image-2.0
    # 注意：不同模型参数结构可能略有不同，这里适配通用结构
    data = {
        "model": model,
        "input": {
            "prompt": prompt
        },
        "parameters": {
            "size": size,
            "n": n
        }
    }
    
    try:
        # 1. 提交任务
        response = requests.post(url, headers=headers, json=data)
        if response.status_code != 200:
            return {
                "success": False,
                "error": f"提交任务失败: {response.text}"
            }
            
        task_data = response.json()
        if "output" not in task_data or "task_id" not in task_data["output"]:
            return {
                "success": False,
                "error": f"无效的响应格式: {response.text}"
            }
            
        task_id = task_data["output"]["task_id"]
        print(f"DashScope 任务已提交，Task ID: {task_id}")
        
        # 2. 轮询任务状态
        task_url = f"https://dashscope.aliyuncs.com/api/v1/tasks/{task_id}"
        start_time = time.time()
        timeout = 120  # 2分钟超时
        
        while True:
            if time.time() - start_time > timeout:
                return {"success": False, "error": "任务超时"}
                
            task_resp = requests.get(task_url, headers={"Authorization": f"Bearer {api_key}"})
            if task_resp.status_code != 200:
                return {"success": False, "error": f"查询状态失败: {task_resp.text}"}
                
            task_result = task_resp.json()
            if "output" not in task_result or "task_status" not in task_result["output"]:
                time.sleep(2)
                continue
                
            status = task_result["output"]["task_status"]
            
            if status == "SUCCEEDED":
                if "results" in task_result["output"] and len(task_result["output"]["results"]) > 0:
                    image_url = task_result["output"]["results"][0]["url"]
                    return {
                        "success": True,
                        "image_url": image_url
                    }
                else:
                    return {"success": False, "error": "任务成功但未返回图片 URL"}
            elif status in ["FAILED", "CANCELED"]:
                return {
                    "success": False, 
                    "error": f"任务失败: {task_result['output'].get('message', '未知错误')}"
                }
            else:
                # PENDING, RUNNING
                time.sleep(2)
                
    except Exception as e:
        return {"success": False, "error": str(e)}
