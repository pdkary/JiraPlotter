class JiraAnalysisDto:
    def __init__(self, committed=None, completed=[], coefficients=[], std_err=0, SSy=0, SSx=0, SSRes=0, r_squared=0):
        self.committed = committed
        self.completed = completed
        self.coefficients = coefficients
        self.std_err = std_err
        self.SSy = SSy
        self.SSx = SSx
        self.SSRes = SSRes
        self.r_squared = r_squared
        self.xbar = 0
        self.ybar = 0
        self.n = 0

    def to_json(self):
        return {
            "n": self.n,
            "committed": self.committed,
            "completed": self.completed,
            "coefficients": self.coefficients.tolist(),
            "std_err": self.std_err,
            "SSy": self.SSy,
            "SSx": self.SSx,
            "SSRes": self.SSRes.item(0),
            "r_squared": self.r_squared.item(0),
            "ybar": self.ybar,
            "xbar": self.xbar
        }

class JiraAnalysisBuilder:
    dto = JiraAnalysisDto()

    def set_committed(self,committed):
        self.dto.committed = committed
        self.dto.n = len(committed)
        self.dto.xbar = sum(committed)/len(committed)
        return self

    def set_completed(self,completed):
        self.dto.completed = completed
        return self

    def set_coefficients(self,coeffs):
        self.dto.coefficients = coeffs
        return self

    def set_std_err(self,err):
        self.dto.std_err = err
        return self

    def set_ssx(self,ssx):
        self.dto.SSx = ssx
        return self

    def set_ssy(self,ssy):
        self.dto.SSy = ssy
        return self

    def set_ssr(self,ssr):
        self.dto.SSRes = ssr
        return self

    def set_r_squared(self,r):
        self.dto.r_squared = r
        return self

    def build(self):
        return self.dto

