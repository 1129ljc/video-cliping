import os
import cv2
import time
import tkinter as tk
import tkinter.messagebox as messagebox
from tkinter import ttk
from tkinter import filedialog
from PIL import ImageTk, Image

config = None


class Config():
    # 播放帧编号
    i_frame = 0
    # 视频文件名称
    file_path = ""
    # 视频文件帧数量
    frame_num = 0
    # 视频帧宽高
    frame_width = 0
    frame_height = 0
    # 视频帧率
    frame_rate = 0
    # 全局视频cv2对象
    capture = None
    capture_insert = None
    # 窗口对象
    UI = None
    canvas = None
    scale = None
    button1 = None
    button2 = None
    button3 = None
    button4 = None
    button5 = None
    button6 = None
    button7 = None
    button8 = None
    button9 = None
    button10 = None
    label0 = None
    label2 = None
    # 窗口宽高
    winWidth = 600
    winHeight = 600
    # 视频播放宽高调整参数
    adjust_w = 0
    adjust_h = 0
    # 视频播放位置调整参数
    x_supplement = 0
    y_supplement = 0
    # 播放线程，已弃用
    processing = None
    # 播放标志位
    playing_flag = 0
    # 读取并播放一帧消耗时间
    frame_time = 0
    # 删除伪造点
    frame_delete_mark = []  # 目前该[]大小为2，后期可扩展单视频的多段删除，删除帧编号区间为[frame_delete_mark[0],frame_delete_mark[1])
    # 插入伪造点
    frame_insert_mark = []  # 目前该[]大小为1，后期可扩展单视频的多点插入，帧插入点为frame_insert_mark[0]


def resize_w_h(frame_width, frame_height):
    '''
    自适应调整视频显示的分辨率
    :param frame_width: 原视频宽度
    :param frame_height: 原视频高度
    :return: 返回resize大小
    '''
    dst_w = 576
    dst_h = 400
    adjust_w = 0
    adjust_h = 0
    if dst_w / dst_h > frame_width / frame_height:
        adjust_w = int(dst_h * (frame_width / frame_height))
        adjust_h = dst_h
    elif dst_w / dst_h < frame_width / frame_height:
        adjust_h = int(dst_w * (frame_height / frame_width))
        adjust_w = dst_w
    elif dst_w / dst_h == frame_width / frame_height:
        adjust_w = dst_w
        adjust_h = dst_h
    return adjust_w, adjust_h


def pixel_position_supplement(adjust_w, adjust_h):
    '''
    调整视频图片的显示坐标
    :param adjust_w:调整后的视频宽度
    :param adjust_h:调整后的视频高度
    :return:返回画布中图像的坐标
    '''
    dst_w = 576
    dst_h = 400
    x_supplement = 0
    y_supplement = 0
    if adjust_w == dst_w:
        y_supplement = int((dst_h - adjust_h) / 2)
    if adjust_h == dst_h:
        x_supplement = int((dst_w - adjust_w) / 2)
    return x_supplement, y_supplement


def openfile():
    config.button1['state'] = 'disabled'
    config.file_path = filedialog.askopenfilename(title=u'Select Video File', filetypes=[('All File', '*.*')])
    if config.file_path == '':
        config.button1['state'] = 'normal'
    elif config.file_path != '':
        config.capture = cv2.VideoCapture(config.file_path)
        config.frame_width = config.capture.get(cv2.CAP_PROP_FRAME_WIDTH)
        config.frame_height = config.capture.get(cv2.CAP_PROP_FRAME_HEIGHT)
        config.frame_num = int(config.capture.get(cv2.CAP_PROP_FRAME_COUNT))
        config.frame_rate = config.capture.get(cv2.CAP_PROP_FPS)
        config.adjust_w, config.adjust_h = resize_w_h(config.frame_width, config.frame_height)
        config.x_supplement, config.y_supplement = pixel_position_supplement(config.adjust_w, config.adjust_h)
        config.label0['text'] = 'Current frame id: 0'
        config.label2['text'] = str(config.frame_num)
        config.scale.set(0, 0)
        config.i_frame = 0
        t1 = time.time()
        config.canvas.delete(tk.ALL)
        ref, frame = config.capture.read()
        cvimage = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        pilImage = cv2.resize(cvimage, (config.adjust_w, config.adjust_h))
        pilImage = Image.fromarray(pilImage)
        tkImage = ImageTk.PhotoImage(image=pilImage)
        config.canvas.create_image(config.x_supplement, config.y_supplement, anchor='nw', image=tkImage)
        t2 = time.time()
        if 1 / config.frame_rate > t2 - t1:
            config.frame_time = round(1 / config.frame_rate - (t2 - t1), 3)
        elif 1 / config.frame_rate <= t2 - t1:
            config.frame_time = t2 - t1
        config.button1['state'] = 'normal'
        config.UI.mainloop()
    return 0


def video_loop():
    while config.i_frame < config.frame_num:
        config.capture.set(cv2.CAP_PROP_POS_FRAMES, config.i_frame)
        ref, frame = config.capture.read()
        if config.playing_flag == 1 and ref is True:
            cvimage = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            pilImage = cv2.resize(cvimage, (config.adjust_w, config.adjust_h))
            pilImage = Image.fromarray(pilImage)
            tkImage = ImageTk.PhotoImage(image=pilImage)
            config.canvas.create_image(config.x_supplement, config.y_supplement, anchor='nw', image=tkImage)
            config.scale.set(config.i_frame / config.frame_num, 0)
            time.sleep(config.frame_time)
            config.i_frame = config.i_frame + 1
            config.label0['text'] = 'Current frame id: {}'.format(str(config.i_frame))
            # config.UI.update_idletasks()
            config.UI.update()
        elif config.playing_flag == 0:
            break
    if int(config.i_frame) == int(config.frame_num):
        config.i_frame = config.i_frame - 1
        messagebox.showinfo(title='message', message='End of the video')
        config.button2['text'] = 'play'


def play():
    config.button2['state'] = 'disabled'
    if config.button2['text'] == 'play':
        config.playing_flag = 1
        config.button2['text'] = 'pause'
        config.button2['state'] = 'normal'
        video_loop()
    elif config.button2['text'] == 'pause':
        config.playing_flag = 0
        '''
        config.capture.set(cv2.CAP_PROP_POS_FRAMES, config.i_frame)
        config.scale.set(config.i_frame)
        ref, frame = config.capture.read()
        cvimage = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        pilImage = cv2.resize(cvimage, (config.adjust_w, config.adjust_h))
        pilImage = Image.fromarray(pilImage)
        tkImage = ImageTk.PhotoImage(image=pilImage)
        config.canvas.create_image(config.x_supplement, config.y_supplement, anchor='nw', image=tkImage)
        '''
        config.button2['text'] = 'play'
        config.button2['state'] = 'normal'
    config.UI.mainloop()
    return 0


def prev_frame():
    '''
    按键前一帧响应
    :return:
    '''
    config.button3['state'] = 'disabled'
    if config.i_frame > 0 and config.i_frame < config.frame_num:
        config.i_frame = config.i_frame - 1
        config.capture.set(cv2.CAP_PROP_POS_FRAMES, config.i_frame)
        ref, frame = config.capture.read()
        cvimage = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        pilImage = cv2.resize(cvimage, (config.adjust_w, config.adjust_h))
        pilImage = Image.fromarray(pilImage)
        tkImage = ImageTk.PhotoImage(image=pilImage)
        config.canvas.create_image(config.x_supplement, config.y_supplement, anchor='nw', image=tkImage)
        config.scale.set(config.i_frame / config.frame_num, 0)
        config.label0['text'] = 'Current frame id:{}'.format(str(config.i_frame))
        config.UI.update()
    elif config.i_frame == 0:
        messagebox.showwarning(title='message', message='Reach frame start')
    config.button3['state'] = 'normal'
    config.UI.mainloop()
    return 0


def next_frame():
    '''
    按键后一帧响应
    :return:
    '''
    config.button4['state'] = 'disabled'
    if config.i_frame >= 0 and config.i_frame < config.frame_num - 1:
        config.i_frame = config.i_frame + 1
        config.capture.set(cv2.CAP_PROP_POS_FRAMES, config.i_frame)
        ref, frame = config.capture.read()
        cvimage = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        pilImage = cv2.resize(cvimage, (config.adjust_w, config.adjust_h))
        pilImage = Image.fromarray(pilImage)
        tkImage = ImageTk.PhotoImage(image=pilImage)
        config.canvas.create_image(config.x_supplement, config.y_supplement, anchor='nw', image=tkImage)
        config.scale.set(config.i_frame / config.frame_num, 0)
        config.label0['text'] = 'Current frame id:{}'.format(str(config.i_frame))
        config.UI.update()
    elif config.i_frame == int(config.frame_num) - 1:
        messagebox.showwarning(title='message', message='End of the video')
    config.button4['state'] = 'normal'
    config.UI.mainloop()
    return 0


def re_init():
    '''
    按键复位响应
    :return:
    '''
    config.button4['state'] = 'disabled'
    config.capture = cv2.VideoCapture(config.file_path)
    config.frame_width = config.capture.get(cv2.CAP_PROP_FRAME_WIDTH)
    config.frame_height = config.capture.get(cv2.CAP_PROP_FRAME_HEIGHT)
    config.frame_num = int(config.capture.get(cv2.CAP_PROP_FRAME_COUNT))
    config.frame_rate = config.capture.get(cv2.CAP_PROP_FPS)
    config.adjust_w, config.adjust_h = resize_w_h(config.frame_width, config.frame_height)
    config.x_supplement, config.y_supplement = pixel_position_supplement(config.adjust_w, config.adjust_h)
    config.label2['text'] = str(config.frame_num)
    config.scale.set(0, 0)
    config.i_frame = 0
    ref, frame = config.capture.read()
    cvimage = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    pilImage = cv2.resize(cvimage, (config.adjust_w, config.adjust_h))
    pilImage = Image.fromarray(pilImage)
    tkImage = ImageTk.PhotoImage(image=pilImage)
    config.canvas.create_image(config.x_supplement, config.y_supplement, anchor='nw', image=tkImage)
    config.label0['text'] = 'Current frame id:0'
    config.button4['state'] = 'normal'
    config.UI.update()
    config.UI.mainloop()
    return 0


def marking2():
    '''
    按键标记响应
    :return:
    '''
    config.button6['state'] = 'disabled'
    if config.button6['text'] == 'label':
        if len(config.frame_delete_mark) == 0:
            config.frame_delete_mark.append(config.i_frame)
            messagebox.showinfo(title='message', message='Frame deletion point 1 has been marked')
            print(config.frame_delete_mark)
        elif len(config.frame_delete_mark) == 1:
            if config.i_frame in config.frame_delete_mark:
                messagebox.showerror(title='error', message='Mark duplicate, please remark')
            else:
                config.frame_delete_mark.append(config.i_frame)
                messagebox.showinfo(title='message', message='Frame deletion point 2 has been marked')
            config.button6['text'] = 'Remove mark'
            print(config.frame_delete_mark)
    elif config.button6['text'] == 'Remove mark' and len(config.frame_delete_mark) == 2:
        config.frame_delete_mark = []
        config.button6['text'] = 'label'
        messagebox.showinfo(title='message', message='Cleared')
    config.button6['state'] = 'normal'
    config.UI.mainloop()
    return 0


def output_delete():
    '''
    按键导出响应，输出删帧视频
    :return:无
    '''
    config.button7['state'] = 'disabled'
    if len(config.frame_delete_mark) == 2:
        file_output = filedialog.asksaveasfile(title=u'Save the video file', filetypes=[("AVI", ".avi")])
        print(file_output.name)
        name_list = file_output.name.split('/')
        if '.avi' not in name_list[-1]:
            name1 = '/'.join(name_list) + '_delete.avi'
            name2 = '/'.join(name_list) + '_deleted.avi'
        else:
            name1 = '/'.join(name_list[0:-1]) + '/' + name_list[-1].split('.')[0] + '_delete.avi'
            name2 = '/'.join(name_list[0:-1]) + '/' + name_list[-1].split('.')[0] + '_deleted.avi'
        print(name1)
        print(name2)
        if file_output is not None:
            fourcc = cv2.VideoWriter_fourcc(*'XVID')
            out1 = cv2.VideoWriter(name1, fourcc, config.frame_rate,
                                   (int(config.frame_width), int(config.frame_height)), True)
            out2 = cv2.VideoWriter(name2, fourcc, config.frame_rate,
                                   (int(config.frame_width), int(config.frame_height)), True)
            i = 0
            config.capture.set(cv2.CAP_PROP_POS_FRAMES, 0)
            while (config.capture.isOpened()):
                ret, frame = config.capture.read()
                if ret == True:
                    if i < config.frame_delete_mark[0] or i >= config.frame_delete_mark[1]:
                        out1.write(frame)
                    else:
                        out2.write(frame)
                    i = i + 1
                else:
                    break
            config.capture.set(cv2.CAP_PROP_POS_FRAMES, config.i_frame)
            out1.release()
            out2.release()
            if os.path.exists(name1) and os.path.exists(name2):
                messagebox.showinfo(title='message', message='Successfully exporting the file: {} and {}'.format(name1, name2))
            else:
                messagebox.showerror(title='error', message='Failed to export the video file')
    else:
        messagebox.showerror(title='error', message='Error marking the frame deletion point')
    config.button7['state'] = 'normal'
    return 0


def location(moveto, pos):
    config.scale.set(pos, 0)
    config.i_frame = int(float(pos) * config.frame_num)
    config.capture.set(cv2.CAP_PROP_POS_FRAMES, config.i_frame)
    config.label0['text'] = 'Current frame id:{}'.format(str(config.i_frame))
    return 0


def marking1():
    config.button8['state'] = 'disabled'
    if config.button8['text'] == 'label' and len(config.frame_insert_mark) == 0:
        config.frame_insert_mark.append(config.i_frame)
        messagebox.showinfo(title='message', message='successfully mark {}'.format(config.i_frame))
        print(config.frame_insert_mark)
        config.button8['text'] = 'Remove marked'
    elif config.button8['text'] == 'Remove marked' and len(config.frame_insert_mark) == 1:
        config.frame_insert_mark = []
        messagebox.showinfo(title='message', message='cleared')
        print(config.frame_insert_mark)
        config.button8['text'] = 'label'
    config.button8['state'] = 'normal'
    return 0


def insert():
    config.button9['state'] = 'disabled'
    insert_file_path = filedialog.askopenfilename(title=u'Select video file', filetypes=[('All File', '*.*')])
    if insert_file_path is None:
        config.button9['state'] = 'normal'
    else:
        config.capture_insert = cv2.VideoCapture(insert_file_path)
        if config.capture_insert is not None:
            messagebox.showinfo(title='message', message='The insert video frame sequence has been read')
        config.button9['state'] = 'normal'
    return 0


def output_insert():
    config.button10['state'] = 'disabled'
    file_output = filedialog.asksaveasfile(title=u'Save the video file', filetypes=[("AVI", ".avi")])
    name = ''
    if file_output is not None:
        print(file_output.name)
        name_list = file_output.name.split('/')
        if '.avi' not in name_list[-1]:
            name = '/'.join(name_list) + '_insert.avi'
        else:
            name = '/'.join(name_list[0:-1]) + '/' + name_list[-1].split('.')[0] + '_insert.avi'
    print(name)
    if len(config.frame_insert_mark) == 1 and config.capture_insert is not None:
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        out = cv2.VideoWriter(name, fourcc, config.frame_rate,
                              (int(config.frame_width), int(config.frame_height)), True)
        config.capture.set(cv2.CAP_PROP_POS_FRAMES, 0)
        for i in range(int(config.frame_num)):
            if config.frame_insert_mark[0] == i:
                for j in range(int(config.capture_insert.get(cv2.CAP_PROP_FRAME_COUNT))):
                    ref, frame = config.capture_insert.read()
                    new_frame = cv2.resize(frame, (int(config.frame_width), int(config.frame_height)))
                    out.write(new_frame)
            else:
                ref, frame = config.capture.read()
                out.write(frame)
        out.release()
        config.capture.set(cv2.CAP_PROP_POS_FRAMES, config.i_frame)
        if os.path.exists(name):
            messagebox.showinfo(title='message', message='Successfully exporting the file {}'.format(name))
        else:
            messagebox.showerror(title='error', message='Failed to export the video file')
    else:
        messagebox.showerror(title='error', message='Empty marked or unread insert frame')
    config.button10['state'] = 'normal'
    return 0


def GUI():
    '''
    初始化窗口
    :return:0
    '''
    global config
    config.UI = tk.Tk()
    config.UI.title("SKLOIS Video Frame Sequence Forgery System")
    screenWidth = config.UI.winfo_screenwidth()
    screenHeight = config.UI.winfo_screenheight()
    x = int((screenWidth - config.winWidth) / 2)
    y = int((screenHeight - config.winHeight) / 2)
    config.UI.geometry("%sx%s+%s+%s" % (config.winWidth, config.winHeight, x, y))
    config.UI.resizable(0, 0)

    config.canvas = tk.Canvas(config.UI, bg='black')
    config.canvas.place(x=12, y=12, width=576, height=400)

    config.label0 = tk.Label(config.UI, text="Current frame id:0", justify='center')
    config.label0.place(x=250, y=413)

    label1 = tk.Label(config.UI, text="0", justify='left')
    label1.place(x=12, y=430)

    config.scale = tk.Scrollbar(config.UI, orient="horizontal", command=location, jump=1)
    config.scale.place(x=25, y=432, width=515, height=20)

    config.label2 = tk.Label(config.UI, text='num', justify='right')
    config.label2.place(x=540, y=430)

    config.button1 = tk.Button(config.UI, text='open-file', command=openfile, relief='raised')
    config.button1.place(x=40, y=460)

    config.button2 = tk.Button(config.UI, text='play', command=play, relief='raised')
    config.button2.place(x=150, y=460)

    config.button5 = tk.Button(config.UI, text='reset', command=re_init, relief='raised')
    config.button5.place(x=200, y=460)

    config.button3 = tk.Button(config.UI, text='previous frame', command=prev_frame, relief='raised')
    config.button3.place(x=300, y=460)

    config.button4 = tk.Button(config.UI, text='next frame', command=next_frame, relief='raised')
    config.button4.place(x=410, y=460)

    tab = ttk.Notebook(config.UI)
    tab.place(x=12, y=500, width=576, height=88)
    frame1 = tk.Frame(tab)
    frame2 = tk.Frame(tab)
    tab.add(frame1, text="frame deletion")
    tab.add(frame2, text="frame insertion")
    frame11 = tk.LabelFrame(frame1, text="Frame deletion: mark two frame numbering points", labelanchor="n")
    frame11.place(x=10, y=2, width=556, height=50)
    frame22 = tk.LabelFrame(frame2, text="Frame insertion: Marking a frame number point and import a frame sequence", labelanchor="n")
    frame22.place(x=10, y=2, width=556, height=50)
    tab.select(frame1)

    config.button6 = tk.Button(frame1, text='label', command=marking2, relief='raised')
    config.button6.place(x=220, y=18)

    config.button7 = tk.Button(frame1, text='export', command=output_delete, relief='raised')
    config.button7.place(x=300, y=18)

    config.button8 = tk.Button(frame2, text='label', command=marking1, relief='raised')
    config.button8.place(x=150, y=18)

    config.button9 = tk.Button(frame2, text='Import insert frame', command=insert, relief='raised')
    config.button9.place(x=240, y=18)

    config.button10 = tk.Button(frame2, text='export', command=output_insert, relief='raised')
    config.button10.place(x=380, y=18)

    config.UI.mainloop()
    if config.capture is not None:
        config.capture.release()
    cv2.destroyAllWindows()
    return 0


if __name__ == '__main__':
    config = Config()
    GUI()
