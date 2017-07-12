'''
Created on 17 Feb 2017

@author: kkuzn
'''
import cx_Oracle


class connectPVSSdb(object):
    '''
    classdocs
    '''
    def __init__(self):
        print "\n\nconnecting..."
        magic     = 'dqm_dcsread_pvss'
        connect   = 'cms_csc_pvss_cond_r/' + magic + '@cms_omds_adg'
        self.orcl = cx_Oracle.connect(connect)
        self.curs = self.orcl.cursor()
        print "          ...done"

    def cursor(self):
        return self.curs
    
    def __del__(self):
        print "\n\nclosing connection..."
        self.orcl.close()
        print "                  ...done"

