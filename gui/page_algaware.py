#!/usr/bin/env python
# -*- coding:utf-8 -*-
#
# Copyright (c) 2018 SMHI, Swedish Meteorological and Hydrological Institute
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).

import tkinter as tk

from PIL import ImageTk

try:
    import ttk
except:
    from tkinter import ttk
from tkinter import messagebox
import sharkpylib.tklib.tkinter_widgets as tkw
import pathlib

import datetime
import calendar

import logging


logger = logging.getLogger(__name__)


class BaseGUI(object):
    """
    """
    def __init__(self):
        super().__init__()
        self._sdate = 'None'
        self._edate = 'None'
        self.current_month = datetime.date.today().replace(day=1)
        self.previous_month = self.current_month - datetime.timedelta(days=1)
        self.previous_month = self.previous_month.replace(day=1)

    def set_sdate(self, dt_obj=None, current_month=None, previous_month=None):
        """
        :param dt_obj:
        :param current_month:
        :param previous_month:
        :return:
        """
        if dt_obj:
            self.sdate = dt_obj
        elif current_month:
            self.sdate = self.current_month
        elif previous_month:
            self.sdate = self.previous_month

    def set_edate(self, dt_obj=None, current_month=None, previous_month=None):
        """
        :param dt_obj:
        :param current_month:
        :param previous_month:
        :return:
        """
        if dt_obj:
            self.edate = dt_obj
        elif current_month:
            end_day = calendar.monthrange(self.current_month.year, self.current_month.month)[1]
            self.edate = self.current_month.replace(day=end_day)
        elif previous_month:
            end_day = calendar.monthrange(self.previous_month.year, self.previous_month.month)[1]
            self.edate = self.previous_month.replace(day=end_day)

    @property
    def sdate(self):
        return self._sdate

    @sdate.setter
    def sdate(self, dt_obj):
        self._sdate = dt_obj.strftime('%Y-%m-%d')

    @property
    def edate(self):
        return self._edate

    @edate.setter
    def edate(self, dt_obj):
        self._edate = dt_obj.strftime('%Y-%m-%d')


class PageAlgaware(BaseGUI, tk.Frame):

    def __init__(self, parent, parent_app, **kwargs):
        super().__init__()
        tk.Frame.__init__(self, parent, **kwargs)
        # parent is the frame "container" in App. contoller is the App class
        self.parent = parent
        self.parent_app = parent_app

        self.main_app = self.parent_app.main_app
        self.user_manager = parent_app.user_manager
        self.user = self.user_manager.user
        # self.settings = parent_app.settings
        self.logger = self.parent_app.logger
        self.log_directory = parent_app.log_directory

        self.handler = None

        # self.default_import_directory = self.settings['directory']['Import directory']
        # self.default_export_directory = self.settings['directory']['Export directory']

    def startup(self):
        self._set_frame()

    def update_page(self):
        # TODO: Update when changing user
        self.user = self.user_manager.user

    def _set_frame(self):
        padx = 5
        pady = 5
        self.grid = dict(padx=padx,
                         pady=pady,
                         sticky='new')
        r = 0
        c = 0
        self.labelframe_timeperiod = tk.LabelFrame(self, text='Time period selection')
        self.labelframe_timeperiod.grid(row=r, column=c, **self.grid)
        c += 1

        self.labelframe_ctd_directory = tk.LabelFrame(self, text='CTD-data directory')
        self.labelframe_ctd_directory.grid(row=r, column=c, **self.grid)

        self.labelframe_lims_path = tk.LabelFrame(self, text='Use data from LIMS')
        self.labelframe_lims_path.grid(row=r+1, column=c, **self.grid)
        c += 1

        self.labelframe_load_data = tk.LabelFrame(self, text='Load data')
        self.labelframe_load_data.grid(row=r, column=c, **self.grid)
        c += 1

        self.labelframe_data = tk.LabelFrame(self, text='Available data')
        self.labelframe_data.grid(row=r, column=c, rowspan=2, **self.grid)
        c += 1

        self.labelframe_plot_figures = tk.LabelFrame(self, text='Plot figures')
        self.labelframe_plot_figures.grid(row=r, column=c, **self.grid)

        # tkw.grid_configure(self, nr_rows=4, nr_columns=4)

        self.frame_grid = {
            'labelframe_timeperiod': {},
            'labelframe_ctd_directory': {},
            'labelframe_load_data': {},
            'labelframe_data': {},
            'labelframe_plot_figures': {},
            }
        self._set_frame_timeperiod()
        self._set_frame_ctd_directory()
        self._set_frame_lims_path()
        self._set_frame_load_data()
        self._set_frame_data()
        self._set_frame_plot_figures()

    def _set_frame_timeperiod(self):
        frame = self.labelframe_timeperiod

        r = 0
        c = 1
        entry_width = 15

        # ----------------------------------------------------------------------
        # Set stringvar
        tk.Label(frame, text='Start date').grid(row=r, column=c, sticky='nw')

        c += 1
        self._set_sdate_entry(col=c, row=r, entry_width=entry_width)

        c += 1
        self.button_set_sdate = tk.Button(frame,
                                          text='Set date from calendar',
                                          command=self._set_sdate_with_calendar)
        self.button_set_sdate.grid(row=r, column=c, **self.grid)

        c -= 2
        r += 1
        tk.Label(frame, text='End date').grid(row=r, column=c, sticky='nw')

        c += 1
        self._set_edate_entry(col=c, row=r, entry_width=entry_width)

        c += 1
        self.button_set_edate = tk.Button(frame,
                                          text='Set date from calendar',
                                          command=self._set_edate_with_calendar)
        self.button_set_edate.grid(row=r, column=c, **self.grid)

        r += 1
        self.button_set_current_month = tk.Button(frame,
                                                  text='Use current month',
                                                  command=self._set_current_month)
        self.button_set_current_month.grid(row=r, column=c, **self.grid)

        r += 1
        self.button_set_previous_month = tk.Button(frame,
                                                   text='Use previous month',
                                                   command=self._set_previous_month)
        self.button_set_previous_month.grid(row=r, column=c, **self.grid)

    def _set_frame_ctd_directory(self):
        """
        :return:
        """
        frame = self.labelframe_ctd_directory
        r = 0
        c = 0
        self.ctd_directory = tkw.DirectoryWidget(frame,
                                                 include_default_button=False,
                                                 row=r, column=c, sticky='nw')

    def _set_frame_lims_path(self):
        """
        :return:
        """
        frame = self.labelframe_lims_path
        r = 0
        c = 0
        self.lims_path = tkw.FilePathWidget(frame, row=r, column=c, sticky='nw')
        r += 1
        self.use_lims = tkw.CheckbuttonWidgetSingle(frame, name='Use this LIMS export', row=r)

    def _set_frame_load_data(self):
        """
        :return:
        """
        frame = self.labelframe_load_data

        r = 0
        c = 0
        # ----------------------------------------------------------------------
        self.button_load_data = tk.Button(frame,
                                          text='Load available data',
                                          command=self._load_data)
        self.button_load_data.grid(row=r, column=c, **self.grid)
        # ----------------------------------------------------------------------

    def _set_frame_data(self):
        frame = self.labelframe_data

        # New test
        self.entry_grid = tkw.EntryGridWidget(frame,
                                              width=420,
                                              height=420,
                                              column=0,
                                              row=0,
                                              # return_direction='vertical',
                                              nr_rows=22,
                                              nr_columns=5,
                                              in_slides=True)

        # col_width = dict((self.header_to_col[item], 5) for item in header)
        header = ['Station', 'Statistics', 'BTL-data', 'CTD-data', 'Dates']
        col_width = {}
        for i, item in enumerate(header):
            col_width[i] = 10
        self.entry_grid.set_width_for_columns(col_width)
        self.entry_grid.insert_values([0]*len(header), range(len(header)), header)

        self.entry_grid.disable_row(0)

    def _set_frame_plot_figures(self):
        """
        :return:
        """
        def add_line(frame, r, col_sp=7):
            return ttk.Separator(frame, orient='horizontal').grid(row=r, column=0, columnspan=col_sp, padx=5, pady=5, sticky='ew')

        frame = self.labelframe_plot_figures
        r = 0
        c = 0
        self.stringvar_file_format = tk.StringVar()
        tk.Label(frame, text='File format:').grid(row=r, column=0, sticky=u'w', padx=5, pady=5)
        self.combobox_widget_file_format = ttk.Combobox(frame,
                                                        textvariable=self.stringvar_file_format,
                                                        state='selected',
                                                        width=9)
        self.combobox_widget_file_format.grid(row=r, column=1, columnspan=2, sticky=u'w', padx=5, pady=5)
        self.combobox_widget_file_format['values'] = ['eps', 'png', 'pdf', 'ALL']

        self.combobox_widget_file_format.set('pdf')

        print(self.combobox_widget_file_format.get())
        # TODO läs ifrån combobox eller stringvar ???
        # self.stringvar_file_format.set('png')
        """
        active, disabled, focus, pressed, selected, background,
            readonly, alternate, invalid
        """
        # ----------------------------------------------------------------------
        r += 1
        add_line(frame, r)
        r += 1
        # ----------------------------------------------------------------------
        preselected = ['The Skagerrak', 'The Kattegat and The Sound', 'The Southern Baltic',
                       'The Western Baltic', 'The Eastern Baltic']
        self.area_options = tkw.CheckbuttonWidget(frame,
                                                  items=preselected,
                                                  pre_checked_items=preselected,
                                                  row=r,
                                                  column=c,
                                                  nr_rows_per_column=5,
                                                  include_select_all=False,
                                                  font=('arial', 8))
        for item in preselected:
            self.area_options.cbutton[item].select()

        r += 1
        add_line(frame, r)
        r += 1
        c = 0
        # ----------------------------------------------------------------------
        self.button_plot_figures = tk.Button(frame,
                                             text='Plot figures',
                                             command=self._plot)
        self.button_plot_figures.grid(row=r, column=c, **self.grid)
        # ----------------------------------------------------------------------

    def _dummy(self):
        pass

    def set_entry_grid_values(self):
        """
        :return:
        """
        x_list = self.parent_app.get_data_xlist()
        self.entry_grid.set_df(x_list.fillna(''), columns=x_list.columns)

    def get_calendar_date(self):
        """
        :return:
        """
        ttkcal = tkw.CalendarWidget()  # master=root)
        ttkcal.pack(expand=1, fill='both')
        ttkcal.wait_window()
        # print('ttkcal.selection', ttkcal.selection)
        return ttkcal.selection

    def _load_data(self):
        """
        :return:
        """
        time_settings = {'start_time': self.sdate,
                         'end_time': self.edate}

        lims_path = self.lims_path.get_value().strip()
        if not self.use_lims.get():
            lims_path = None
            logger.info('Data source is Archive')
        elif self.use_lims.get() and not lims_path:
            messagebox.showerror('Loading available data', 'No LIMS file shosen!')
            return
        elif self.use_lims.get() and not pathlib.Path(lims_path).exists():
            messagebox.showerror('Loading available data', 'Invalid LIMS path!')
            return
        else:
            logger.info('Data source is LIMS')

        self.parent_app.load_data(time_settings,
                                  ctd_directory=self.ctd_directory.get_value(),
                                  lims_path=lims_path)
        self.set_entry_grid_values()

    def _plot(self):
        """
        :return:
        """
        figures_to_plot = self.area_options.get_checked_item_list()
        for figure_key in figures_to_plot:
            self.parent_app.plot(figure_key, save_as_format=self.file_formats)

    def _set_sdate_with_calendar(self):
        """
        :return:
        """
        date = self.get_calendar_date()
        self.set_sdate(dt_obj=date)
        self.update_sdate_entry()

    def _set_edate_with_calendar(self):
        """
        :return:
        """
        date = self.get_calendar_date()
        self.set_edate(dt_obj=date)
        self.update_edate_entry()

    def _set_current_month(self):
        """
        :return:
        """
        self.set_sdate(current_month=True)
        self.set_edate(current_month=True)
        self.update_sdate_entry()
        self.update_edate_entry()

    def _set_previous_month(self):
        """
        :return:
        """
        self.set_sdate(previous_month=True)
        self.set_edate(previous_month=True)
        self.update_sdate_entry()
        self.update_edate_entry()

    def _set_sdate_entry(self, row=None, col=None, entry_width=None):
        """
        :param col:
        :param row:
        :return:
        """
        self.frame_grid['labelframe_timeperiod'].setdefault('sdate_entry', dict())
        self.frame_grid['labelframe_timeperiod']['sdate_entry'].setdefault('row', row)
        self.frame_grid['labelframe_timeperiod']['sdate_entry'].setdefault('col', col)
        self.frame_grid['labelframe_timeperiod']['sdate_entry'].setdefault('entry_width', entry_width)

        self.stringvar_sdate = tk.StringVar()
        self.entry_sdate = tk.Entry(self.labelframe_timeperiod,
                                    textvariable=self.stringvar_sdate,
                                    width=entry_width)
        self.entry_sdate.grid(row=self.frame_grid['labelframe_timeperiod']['sdate_entry'].get('row'),
                              column=self.frame_grid['labelframe_timeperiod']['sdate_entry'].get('col'),
                              **self.grid)
        self.entry_sdate.insert(0, self.sdate)
        self.entry_sdate.config(state='disable')

    def _set_edate_entry(self, row=None, col=None, entry_width=None):
        """
        :param col:
        :param row:
        :return:
        """
        self.frame_grid['labelframe_timeperiod'].setdefault('edate_entry', dict())
        self.frame_grid['labelframe_timeperiod']['edate_entry'].setdefault('row', row)
        self.frame_grid['labelframe_timeperiod']['edate_entry'].setdefault('col', col)
        self.frame_grid['labelframe_timeperiod']['edate_entry'].setdefault('entry_width', entry_width)

        self.stringvar_edate = tk.StringVar()
        self.entry_edate = tk.Entry(self.labelframe_timeperiod,
                                    textvariable=self.stringvar_edate,
                                    width=entry_width)
        self.entry_edate.grid(row=self.frame_grid['labelframe_timeperiod']['edate_entry'].get('row'),
                              column=self.frame_grid['labelframe_timeperiod']['edate_entry'].get('col'),
                              **self.grid)
        self.entry_edate.insert(0, self.edate)
        self.entry_edate.config(state='disable')

    def update_sdate_entry(self):
        """
        :return:
        """
        self.entry_sdate.destroy()
        self._set_sdate_entry()

    def update_edate_entry(self):
        """
        :return:
        """
        self.entry_edate.destroy()
        self._set_edate_entry()

    @property
    def file_formats(self):
        """
        :return:
        """
        print('returning %s as file format' % self.stringvar_file_format.get())
        # print('self.combobox_widget_file_format.get_value()', self.combobox_widget_file_format.get_value())
        # fmts = self.stringvar_file_format.get()
        # print('fmts', fmts, type(fmts))
        # if fmts == 'ALL':
        #     fmts = ['png', 'pdf', 'eps']
        fmts = ['png', 'pdf']
        return fmts

    def plot_image(self, frame, row, col):
        """
        from PIL import Image, ImageTk
        dimensions_of_image = "image size: %dx%d" % (photo.width(), photo.height())
        """
        path = '//winfs-proj/proj/havgem/Johannes_Johansson/mixed/pictures/algaware.png'
        # try:
        # image = Image.open(path)
        # image = image.resize((320, 87), Image.ANTIALIAS)

        # photo = ImageTk.PhotoImage(image)
        label = tk.Label(frame)
        # label = tk.Label(frame, image=photo)
        label.img = ImageTk.PhotoImage(file=path)  # keep a reference!
        label.config(image=label.img)
        label.pack()
        # label.grid(row=row, column=col)

        # master = Tk()
        # label = Label(master)
        # label.img = PhotoImage(file='foo.png')
        # label.config(image=label.img)
        # label.pack()
        # except:
        #     pass