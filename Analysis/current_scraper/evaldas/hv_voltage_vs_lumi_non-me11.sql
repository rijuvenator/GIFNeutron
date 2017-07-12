select    
    change_date,
    dpname,
    max(value) hv_voltage,
    max(l.instlumi) instantaneous_luminosity
from
  cms_csc_pvss_cond.csc_hv_v_data d join cms_csc_pvss_cond.dp_name2id dp on (dp.id = d.DPID) join CMS_RUNTIME_LOGGER.LUMI_SECTIONS l on (l.starttime < d.change_date and l.stoptime > d.change_date)
where
  change_date > to_date('2016.10.10 14:11', 'YYYY-MM-DD HH24:MI') and change_date < to_date('2016.10.11 06:57', 'YYYY-MM-DD HH24:MI') and not dpname like '%_Mch_%' and value is not null
  -- something like this would probably work to select by LHC fill number, just uncomment the next line and comment the previous line (but I'm not sure if oracle will optimize this type of query properly, so it may run very very long, even indefinitely -- if that's the case, we can do some tricks to make it fast)
  --lhcfill=5394 and not dpname like '%_Mch_%' and value is not null
group by
  change_date, dpname