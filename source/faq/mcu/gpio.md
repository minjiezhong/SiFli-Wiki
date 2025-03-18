# 1 GPIO相关
## 1.1 GPIO操作和调试方法
1, RTT操作系统DRV层的操作方法<br>
a，sf32lb55x内包含Hcpu PA口和Lcpu PB口，Hcpu可以完全操作Lcpu的资源，包括PB口，<br>
但是Lcpu不能直接读写PA口，否则会出现Hardfault<br>
b，sf32lb55x 的GPIO已经封装成了标准的rt-thread的设备PIN，在rt-thread操作系统起来后，就可以直接参考rt-thread官网操作GPIO
如下链接:<br> [PIN设备 (rt-thread.org)](https://www.rt-thread.org/document/site/#/)：
<br>![alt text](./assets/gpio/gpio001.png)<br> 
PIN设备统一操作GPIO,PA,PB口统一进行了编排，PA口为GPI00到GPIO95,PB口为GPIO96开始.<br>
例如操作PB口，需要加上96，比如操作PB48<br>
```c
rt_pin_mode(144, PIN_MODE_INPUT_PULLUP);//配置PB48为输入口（48+96=144），注意此处配置上下拉，目前代码没有生效，需用HAL函数配置
curr_state = rt_pin_read(144); /* 读 PB48口状态 */
rt_pin_attach_irq(144, PIN_IRQ_MODE_FALLING, chsc5816tp_irq_handler, RT_NULL);/*配置为下降沿触发，中断函数为chsc5816tp_irq_handler */
rt_pin_irq_enable(144, 1);/* 启动 PB48 GPIO中断*/
```
比如操作PA78<br>
```c
rt_pin_mode(78, PIN_MODE_OUTPUT);
rt_pin_write(78, 0);/* PA78 输出低 */
rt_pin_mode(79, PIN_MODE_INPUT_PULLUP);/* 配置PA79为输入口，注意此处配置上下拉，目前代码没有生效，需用HAL函数配置 */
if (1 == rt_pin_read(79)) /* 读PA79状态 */
```

**注意:**<br>
 采用pin的设备读写操作前，需要rt_pin_mode先设置mode，另外从standby唤醒，软件会恢复到最初的电平状态.

2，HAL层GPIO的操作<br>
在RTT操作系统还没起来时，比如drv_io.c的底层可以直接调用HAL接口的GPIO函数.<br>
比如设置PA，PB的函数，PA或者PB需用一个参数来区分：<br>
```c
HAL_PIN_Set(PAD_PA03，GPIO_A3,PIN_NOPULL, 1);//设置PA03为GPIO模式，无上下拉
```
设置输入输出模式:<br>
```c
HAL_PIN_SetMode(PAD_PA01, 1, PIN_DIGITAL_OUTPUT_NORMAL); //PA01设为输出模式，无上下拉，
```
输出高低:<br>
```c
BSP_GPIO_Set(3, 0, 1); //PA03输出低
BSP_GPIO_Set(3, 0, 0); //PB03输出低
```
读取IO数值:<br>
```
int value;
value = HAL_GPIO_ReadPin((GPIO_TypeDef *)hwp_gpio1, 48); //读PA48的值：
value = HAL_GPIO_ReadPin((GPIO_TypeDef *)hwp_gpio2, 48); //读PB48的值：
value = HAL_PBR_ReadPin(1); //读PBR1的值：
```
**注意:**<br> 
HAL层操作GPIO，要参数来区分hcpu和lcpu，因此不能再用DRV层把PB48 当作96+48来操作<br>

3， GPIO调试<br>
推荐在hcpu的console平台， pin命令行来查看修改gpio状态，
比如:
```
pin status all //查看所有GPIO状态.
pin status 120 //查看120-96=24 PB24的状态41
pin mode 120 0 //设置PB24为输出mode
pin write 78 1 //设置PA78输出高
pin mux 106 2 //设置106-96=10 PB10为功能2 I2C4_SDA功能
```
<br>![alt text](./assets/gpio/gpio002.png)<br>  

## 1.2 55X系列 PA口在睡眠唤醒后会有电平波动
    HCPU PA口睡眠唤醒后会先恢复到芯片默认的上下拉，如下图: <br>
<br>![alt text](./assets/gpio/gpio003.png)<br>  
这个时候用户程序还没有跑起来， 然后再执行代码pinmux.c文件BSP_IO_Init里面设置的值，<br>
所以HCPU GPIO如果睡眠的时候电平与默认上下拉不一致，唤醒后有可能存在10ms左右的跳变；<br>
LCPU PB口睡眠唤醒后，唤醒前的值可以一直保存到BSP_IO_Init函数执行，所以只要在BSP_IO_Init设置好GPIO口状态，LCPU GPIO 的值睡眠是可以保持的.<br>
比如 PA03你想开机后一直保持高电平，但由于PA03默认是下拉的，所以睡眠唤醒后会有10ms左右的低电平，再实际使用中，你需要找个默认是上拉的脚来替换PA03，比如PA10.<br>

**备注:** <br>
56X,52X系列PA口不存在此问题

## 1.3 TP的驱动 IRQ中断怎么配置
1，Menuconfig配置 <br>
配置完， 会在rtconfig.h中生成: <br>
```c
#define TOUCH_IRQ_PIN 79
```
<br>![alt text](./assets/gpio/gpio004.png)<br>  
2，pinmux.c中，需要确认该IO口的模式和上下拉状态：<br>
```c
HAL_PIN_Set(PAD_PA79, GPIO_A79, PIN_NOPULL, 1); // GPIO模式，无上拉，
```
3，在drv_touch.c会用到该定义，驱动可以直接使用drv_touch.c中两个函数：<br>
```c
    rt_touch_irq_pin_attach(PIN_IRQ_MODE_FALLING, cst816_irq_handler, NULL);
    rt_touch_irq_pin_enable(1);
```
或者自己在初始化函数中定义该中断：<br>
```c
    rt_pin_mode(TOUCH_IRQ_PIN, PIN_MODE_INPUT); //配置为input
    rt_pin_attach_irq(TOUCH_IRQ_PIN, PIN_IRQ_MODE_FALLING, (void *) cst816_irq_handler,(void *)(rt_uint32_t)TOUCH_IRQ_PIN);//配置下降沿中断和中断回调函数
    rt_pin_irq_enable(TOUCH_IRQ_PIN, 1); //使能中断
```
4，Hcpu的串口输入命令：pin status 79 确认该配置是否正确。<br>

## 1.4 如何detach touch irq
在touch驱动deinit函数中，在detach irq之前，需要先关闭该pin的中断：<br>
```c
static rt_err_t deinit(void)
{
    rt_pin_irq_enable(TOUCH_IRQ_PIN, 0); //disable irq
    rt_pin_detach_irq(TOUCH_IRQ_PIN);
...
```
## 1.5 为什么PA55口为默认下拉口PD，但是上电我不做任何操作，PA55测试为高电平?
根本原因: 客户的OTA代码中， 有对PA55进行拉高操作.<br>
让客户在用户程序pinmux.c中，添加`__asm("B .");`断点命令，<br>
<br>![alt text](./assets/gpio/gpio005.png)<br>   
测试PA55口，为高，
```
mem32 0x50000038 20 读了相应的寄存器，有输出高的操作，
```
jlink输入r，让芯片复位，<br>
在读寄存器值恢复正常， PA55电平也正常，<br>
由于用户程序是从0x10060000开始跑的， 复位后 是从0x10020000 OTA的代码开始跑， 然后跳到用户的0x1006000的代码， 而OTA代码drv_io.c中操作了，PA55，导致该现象.

## 1.6 55系列MCU复用USB的PA01/PA03漏电风险
通常情况下，建议客户不使用PA01，<br>
由于PA01，PA03是复用USB口功能， PA01，PA03当作GPIO使用时， 要特别谨慎；<br>
1， PA01内部在active，light_sleep模式下存在18K的下拉电阻，输出高电平，否则存在漏电，standby，deep_sleep模式下18k下拉电阻不生效.<br>
2，在standby模式下， PA01，PA03输出电平不一致， 会出现通过USB电路，出现漏电流，
具体而言，当满足以下条件时会存在漏电约20uA: <br>
a，进入standby睡眠 <br>
b，PA01和PA03配置电平不一致(其中一个输出高或上拉，另一个输出低或下拉)。该漏电大小是不确定的值，可能随板子或环境变化有差异。<br>
c，消除漏电的补丁方案：当进入睡眠时，使两个IO的电平一致，或至少将其中一个置为高阻状态(无上下拉)。<br>
d，细节上有一些补充：1. PA01的下拉电阻在standby和deep_sleep模式下反而不会漏电，是在active或light_sleep的时候才漏 2. 高阻不仅是我们的配置，也要板子上没有上下拉，<br>
可以采用下面方式输出高阻态:<br>
```c
HAL_PIN_Set_Analog(PAD_PA01,1); /* 模拟输入为Func10，关断GPIO输出，输入使能IE关闭，即为高阻态 */
HAL_PIN_Set_Analog(PAD_PA03,1);
```
## 1.7 55系列MCU-PB47/PB48配置32768时钟输出

使用前，需确认MCU这边贴了32768晶体，并关闭了`#define LXT_DISABLE 1`<br>
另外需要修改两点：
1，使能标志位，以PB47为例：<br>
```c
     #define LPSYS_AON_DBGMUX_PB47_SEL_LPCLK  (0x1UL << LPSYS_AON_DBGMUX_PB47_SEL_Pos)
        MODIFY_REG(hwp_lpsys_aon->DBGMUX,LPSYS_AON_DBGMUX_PB47_SEL_Msk,LPSYS_AON_DBGMUX_PB47_SEL_LPCLK);
```
 2，如果需要睡眠的时候保持32k输出，需要屏蔽如下截图部分。<br>
    因为如果LPSYS_AON_ANACR_PB_AON_ISO置1，唤醒管脚PB43~PB48睡眠时就能保持电平，但代价就是不能输出32k或者lptim3控制的波形。屏蔽后PB43~PB48这几个唤醒管脚睡眠期间不能保持电平，所以不能用作GPIO输出管脚 
<br>![alt text](./assets/gpio/gpio006.png)<br>      
3，需要注意：<br>
因为步骤2，PB为了输出32k关闭了standy下IO保持功能， 因此PB口的唤醒脚PB43-48在standby模式下，由于内部上下拉不再生效，外部要必须给确定电平或者视外部连接设为输出高或者低，防止standby模式下PB43-PB48漏电。

## 1.8 增加PB25为按键KEY2 
1，Lcpu中 menuconfig  → Sifli middleware → Enable button library 设置按键个数为2<br>
2，Lcpu中 menuconfig  → Select board peripherals → Key config 设置KEY2对应GPIO为121（96+25）
<br>![alt text](./assets/gpio/gpio007.png)<br>   
3，Lcpu中 menuconfig  → Sifli middleware → Enable button library 设置按键个数为2<br>
4，Lcpu中 menuconfig  → Select board peripherals → Key config 设置KEY2对应GPIO为121（96+25）<br>
5，Lcpu中，在sensor_service.c 函数init_pin中配置KEY2的初始化和唤醒源
<br>![alt text](./assets/gpio/gpio008.png)<br>   
6，Hcpu中，在watch_demo.c函数init_pin中配置KEY2的消息订阅
<br>![alt text](./assets/gpio/gpio009.png)<br>  

## 1.9 提高GPIO驱动能力 
DS0,DS1位都置1，驱动能力最强<br>
```c
HAL_PIN_Set_DS0(PAD_PA10,1,1); //PA10 DS0置1
HAL_PIN_Set_DS1(PAD_PA10,1,1); //PA10 DS1置1
HAL_PIN_Set_DS1(PAD_PB16,0,1); //PB16 DS1置1
```

## 1.10 GPIO配置为高阻模式
如下，设置该IO为模拟输入态，该IO口对外即为高阻态<br>
```c
HAL_PIN_Set_Analog(PAD_PA17, 1); //PA17 设置为模拟输入，对外高阻
HAL_PIN_Set_Analog(PAD_PB27, 0);  //PB27 设置为模拟输入，对外高阻
```
从高阻态恢复为原IO状态，如下：<br>
```c
HAL_PIN_Set(PAD_PA17, GPIO_A17, PIN_NOPULL, 1);
HAL_PIN_Set(PAD_PB27, GPIO_B27, PIN_NOPULL, 0);
HAL_PIN_SetMode(PAD_PA17, 1, PIN_DIGITAL_IO_PULLDOWN);  //sdk版本v2.2.0后，不再需要
HAL_PIN_SetMode(PAD_PB27, 0, PIN_DIGITAL_IO_PULLUP); //sdk版本v2.2.0后，不再需要
```
HAL_PIN_Set_Analog会把IO的IE位置0，如果只调用的HAL_PIN_Set函数配置，该函数不会操作IE位，此时输入不能用，需要IO恢复成输入口使用，还需调用HAL_PIN_SetMode函数配置，把IE为恢复为1。<br>

**注意：**<br>
sdk版本v2.2.0后，在HAL_PIN_Set函数中，已经添加IE恢复为1操作，不需要再多添加HAL_PIN_SetMode函数

## 1.11 52X PA22/PA23 32K晶体复用IO, I2C无法输出波形问题
原因：52X，其他IO的IE默认是1，而32k的两个IO是IE为默认为0，<br>
默认的流程，HAL_PIN_Set函数，不会把IE置1，而PA22,23这两个IO，而默认IE是0，所以不能输出波形
<br>![alt text](./assets/gpio/gpio010.png)<br>   
解决方法：<br>
添加HAL_PIN_SetMode函数把IO设置为正常IO后，IE位会置1，I2C可以正常输出。
<br>![alt text](./assets/gpio/gpio011.png)<br>  

**注意：**<br>
56X的PA55,PA56两个32K IO的IE位默认位1，不存在此问题。<br>
sdk版本v2.2.0后，在HAL_PIN_Set函数中，已经添加IE恢复为1操作，不需要再多添加HAL_PIN_SetMode函数
