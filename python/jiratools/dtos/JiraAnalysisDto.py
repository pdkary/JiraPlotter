class JiraAnalysisDto:
    def __init__(self, committed=None, completed=[], coefficients=[], std_err=0, SSy=0, SSx=0, SSRes=0, r_squared=0,
                 xbar=0, ybar=0):
        self.committed = committed
        self.completed = completed
        self.coefficients = coefficients
        self.std_err = std_err
        self.SSy = SSy
        self.SSx = SSx
        self.SSRes = SSRes
        self.r_squared = r_squared
        self.xbar = xbar
        self.ybar = ybar

    def set_committed(self, committed):
        self.committed = committed
        return self

    def set_completed(self, completed):
        self.completed = completed
        return self

    def set_coefficients(self, coefficients):
        self.coefficients = coefficients
        return self

    def set_stderr(self, err):
        self.std_err = err
        return self

    def set_ssy(self, ssy):
        self.SSy = ssy
        return self

    def set_ssx(self, ssx):
        self.SSx = ssx
        return self

    def set_r_squared(self, r_squared):
        self.r_squared = r_squared
        return self

    def set_ssr(self, ssr):
        self.SSRes = ssr
        return self

    def set_xbar(self, xbar):
        self.xbar = xbar
        return self

    def set_ybar(self, ybar):
        self.ybar = ybar
        return self

    def to_json(self):
        return {
            "committed": self.committed,
            "completed": self.completed,
            "coefficients": self.coefficients.tolist(),
            "std_err": self.std_err,
            "SSy": self.SSy,
            "SSx": self.SSx,
            "SSRes":self.SSRes.item(0),
            "r_squared": self.r_squared.item(0),
            "ybar":self.ybar,
            "xbar":self.xbar
        }
