# Copyright (C) 2016-2018  Kevin O'Connor <kevin@koconnor.net>

import flask
import optparse, datetime

class KlipperLogAnalyzer():
   MAXBANDWIDTH=25000.
   MAXBUFFER=2.
   STATS_INTERVAL=5.
   TASK_MAX=0.0025
   APPLY_PREFIX = ['mcu_awake', 'mcu_task_avg', 'mcu_task_stddev', 'bytes_write',
                   'bytes_read', 'bytes_retransmit', 'freq', 'adj']
                   
   def __init__(self, log_file):
      self.log_file = log_file

   def analyze(self):
      data = self.parse_log(self.log_file, None)
      if not data:
         result = dict(error= "Couldn't parse \"{}\"".format(self.log_file))
      else:
         result = self.plot_mcu(data, self.MAXBANDWIDTH)
      #if options.frequency:
      #    plot_frequency(data, outname, options.mcu)
      #    return
      return result

   def parse_log(self, logname, mcu):
      if mcu is None:
         mcu = "mcu"
      mcu_prefix = mcu + ":"
      apply_prefix = { p: 1 for p in self.APPLY_PREFIX }
      
      f = open(logname, 'rb')
      out = []
      
      for line in f:
         parts = line.split()
         if not parts or parts[0] not in ('Stats', 'INFO:root:Stats'):
            #if parts and parts[0] == 'INFO:root:shutdown:':
            #    break
            continue
         prefix = ""
         keyparts = {}
         for p in parts[2:]:
            if '=' not in p:
               prefix = p
               if prefix == mcu_prefix:
                  prefix = ''
               continue
            name, val = p.split('=', 1)
            if name in apply_prefix:
               name = prefix + name
            keyparts[name] = val
         if keyparts.get('bytes_write', '0') == '0':
            continue
         keyparts['#sampletime'] = float(parts[1][:-1])
         out.append(keyparts)
      f.close()
      return out

   def find_print_restarts(self, data):
      runoff_samples = {}
      last_runoff_start = last_buffer_time = last_sampletime = 0.
      last_print_stall = 0
      for d in reversed(data):
         # Check for buffer runoff
         sampletime = d['#sampletime']
         buffer_time = float(d.get('buffer_time', 0.))
         if (last_runoff_start and last_sampletime - sampletime < 5
            and buffer_time > last_buffer_time):
            runoff_samples[last_runoff_start][1].append(sampletime)
         elif buffer_time < 1.:
            last_runoff_start = sampletime
            runoff_samples[last_runoff_start] = [False, [sampletime]]
         else:
            last_runoff_start = 0.
         last_buffer_time = buffer_time
         last_sampletime = sampletime
         # Check for print stall
         print_stall = int(d['print_stall'])
         if print_stall < last_print_stall:
            if last_runoff_start:
               runoff_samples[last_runoff_start][0] = True
         last_print_stall = print_stall
      sample_resets = {sampletime: 1 for stall, samples in runoff_samples.values()
                        for sampletime in samples if not stall}
      return sample_resets

   def plot_mcu(self, data, maxbw):
      # Generate data for plot
      basetime = lasttime = data[0]['#sampletime']
      lastbw = float(data[0]['bytes_write']) + float(data[0]['bytes_retransmit'])
      sample_resets = self.find_print_restarts(data)
      times = []
      bwdeltas = []
      loads = []
      awake = []
      hostbuffers = []
      for d in data:
         st = d['#sampletime']
         timedelta = st - lasttime
         if timedelta <= 0.:
            continue
         bw = float(d['bytes_write']) + float(d['bytes_retransmit'])
         if bw < lastbw:
            lastbw = bw
            continue
         load = float(d['mcu_task_avg']) + 3*float(d['mcu_task_stddev'])
         if st - basetime < 15.:
            load = 0.
         pt = float(d['print_time'])
         hb = float(d['buffer_time'])
         if hb >= self.MAXBUFFER or st in sample_resets:
            hb = 0.
         else:
            hb = 100. * (self.MAXBUFFER - hb) / self.MAXBUFFER
         hostbuffers.append(hb)
         #times.append(datetime.datetime.utcfromtimestamp(st))
         times.append(st)
         bwdeltas.append(100. * (bw - lastbw) / (maxbw * timedelta))
         loads.append(100. * load / self.TASK_MAX)
         awake.append(100. * float(d.get('mcu_awake', 0.)) / self.STATS_INTERVAL)
         lasttime = st
         lastbw = bw
         
      result = dict(
         times= times,
         bwdeltas= bwdeltas,
         loads= loads,
         awake= awake,
         buffers= hostbuffers
      )
      return result
      
   def plot_frequency(self, data, mcu):
      all_keys = {}
      for d in data:
         all_keys.update(d)
      one_mcu = mcu is not None
      graph_keys = { key: ([], []) for key in all_keys
                   if (key in ("freq", "adj") or (not one_mcu and (
                           key.endswith(":freq") or key.endswith(":adj")))) }
      basetime = lasttime = data[0]['#sampletime']
      for d in data:
         st = d['#sampletime']
         for key, (times, values) in graph_keys.items():
            val = d.get(key)
            if val not in (None, '0', '1'):
               times.append(st)
               values.append(float(val))
