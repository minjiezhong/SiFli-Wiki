# 13 UART相关
## 13.1 UART1不进入RX中断回调函数问题
根本原因：<br>
1，UART FIFO只有一个字节，系统如果忙的话，一个byte长度大约10bit, 115200需要大约1us, 收到中断1us之内不清空FIFO, 就会overflow;<br>
2，USART1_IRQHandler中断能进来，但是因为有错误，所以没有上层回调，上层回调只是在正常收到数据才会有。由于Uart1用于控制音频蓝牙，改成Segger打印，系统轮询，有可能导致来不及清RX中断。<br>
解决方案：<br>
改成DMA RX中断。<br>
 rt_device_open(g_bt_uart, RT_DEVICE_FLAG_INT_RX);
改成
 rt_device_open(g_bt_uart, RT_DEVICE_FLAG_DMA_RX);
