# 1 Log调试
## 1.1 Hcpu没有log出来
1，menuconfig→ RTOS → RT-Thread Kernel → Kernel Device Object→uart1配置为uart1
2，menuconfig → RTOS → RT-Thread Components → Utilities→Enable ulog打开
TIPS: menuconfig中可以输入 "/" 搜索"ulog"
3,pinmux.c中UART1的配置是否正确配置为UART1配置，常见的是开启了BSP_ENABLE_QSPI3，如下图：
<br>![alt text](./assets/log/log001.png)<br>    

## 1.2 Lcpu没有log出来
如下配置后， 依然没有打印，<br>
  1，menuconfig→ RTOS → RT-Thread Kernel → Kernel Device Object→uart3配置为uart3<br>
  2，menuconfig → RTOS → RT-Thread Components → Utilities→Enable ulog打开<br>
  3，确认hcpu中，在menuconfig→ RTOS → RT-Thread Kernel → Kernel Device Object→uart1 这里没有没有配置为uart3，不然会冲突.<br>
  4, 确认pinmux.c中，PB45,PB46这两个UART3的模式配置正确，默认配置正确，如下：<br>
  ```c
    HAL_PIN_Set(PAD_PB45, USART3_TXD, PIN_NOPULL, 0);           // USART3 TX/SPI3_INT
    HAL_PIN_Set(PAD_PB46, USART3_RXD, PIN_PULLUP, 0);           // USART3 RX
```	
其他原因1: <br>
用的V0.9.9\example\rt_driver\project\ec-lb551工程，ble线程没有开启， 导致Lcpu程序没有加载，<br>
<br>![alt text](./assets/log/log002.png)<br>       
解决方案:<br>
打开ble线程或者单独调用函数lcpu_power_on(); 启动lcpu的代码.<br>
其他原因2：<br>
```
example\multicore\ipc_queue\
example\pm\coremark\
```
这些工程，需要在HCPU的console里发送命令`lcpu on`启动LCPU，启动成功后可以在LCPU的console上看到启动log<br>
解决方案：<br>
相应的工程下，有readme.txt文件，可以参考里面的内容发命令打开Lcpu<br>

## 1.3 代码中打印寄存器方法
直接地址读操作:
```c
static uint32_t pinmode19;
pinmode19= *(volatile uint32_t *)0x4004304c; //读取寄存器0x4004304c的值
uint32_t reg_printf= *(volatile uint32_t *)0x50016000; //打印寄存器0x50016000的值
rt_kprintf("0x50016000:0x%x\n",reg_printf);
```
直接地址写操作：
```c
#define _WWORD(reg,value) \
{ \
    volatile uint32_t * p_reg=(uint32_t *) reg; \
    *p_reg=value; \
}
_WWORD(0x40003050,0x200);  //PA01 pinmux寄存器写值0x00000200
```
寄存器定义读操作：
```c
rt_kprintf("hwp_hpsys_rcc->CFGR:0x%x\n",hwp_hpsys_rcc->CFGR);
uint32_t reg_printf= hwp_hpsys_rcc->CFGR; //打印寄存器
rt_kprintf("hwp_hpsys_rcc->CFGR:0x%x\n",reg_printf);
```
寄存器定义写操作：
```c
hwp_hpsys_rcc->CFGR = 0x40003050;//直接写值
MODIFY_REG(hwp_pmuc->LPSYS_SWR, PMUC_LPSYS_SWR_PSW_RET_Msk,
			MAKE_REG_VAL(1, PMUC_LPSYS_SWR_PSW_RET_Msk, PMUC_LPSYS_SWR_PSW_RET_Pos)); //只修改PMUC_LPSYS_SWR_PSW_RET_Msk的值为1，其他地方不变；

```
