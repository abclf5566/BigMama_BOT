import asyncio
import trade_data 

async def main():
    # 运行异步模块中的主函数
    await trade_data.main()

# 运行主函数
asyncio.run(main())
