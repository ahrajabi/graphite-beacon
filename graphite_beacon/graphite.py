import rpy2.robjects as robjects

Rtxt = '''
library(AnomalyDetection)
f_ts <- function(timestamp , count) {
    timestamp = as.numeric(timestamp)
    count = as.numeric(count)
    data <- t(matrix( c(rbind(timestamp,count))  , nrow=2 ))
    data <- data.frame(data)
    names(data) <- c('timestamp' , 'count')
    res = AnomalyDetectionTs(data, max_anoms=0.02, direction='both' , only_last='hr')
    return(res)
}
f_vec <- function(count) {
    count = as.numeric(count)
    res = AnomalyDetectionVec(count, period=20,max_anoms=0.2 , direction='both', only_last=TRUE)
    return(res$anoms)
}
'''

class GraphiteRecord(object):

    def __init__(self, metric_string):

        meta, data = metric_string.split('|')
        self.target, start_time, end_time, step = meta.rsplit(',', 3)
        self.start_time = int(start_time)
        self.end_time = int(end_time)
        self.step = int(step)
        self.datalist = data.rsplit(',')
        self.timeseries = [self.start_time+i*self.step for i in range(len(self.datalist))]

        self.values = list(self._values( self.datalist ))
        self.datalist = list(self._valuesTs(self.datalist))
        self.lgg =  self.timeseries
        if len(self.values) == 0:
            self.empty = True
        else:
            self.empty = False
        robjects.r(Rtxt)

        self.AnomalyDetectionVec = robjects.globalenv['f_vec']
        self.AnomalyDetectionTs = robjects.globalenv['f_ts']

    @staticmethod
    def _values(values):
        for value in values:
            try:
                yield float(value)
            except ValueError:
                continue

    @staticmethod
    def _valuesTs(values):
        for value in values:
            try:
                yield float(value)
            except ValueError:
                yield 0.0

    @property
    def average(self):
        return self.sum / len(self.values)

    @property
    def last_value(self):
        return self.values[-1]

    @property
    def sum(self):
        return sum(self.values)

    @property
    def twitter(self):
        anoms =  self.AnomalyDetectionVec(self.datalist)
        print anoms
        if anoms:
            return len(anoms[0])
        return 0

