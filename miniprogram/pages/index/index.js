
// 策略监控小程序首页
const API_BASE = 'http://49.232.79.54:8000/api';

Page({
  data: {
    status: '加载中...',
    balance: '¥0',
    todayPnl: '¥0',
    todayPnlClass: '',
    closedPnl: '¥0',
    totalPos: 0,
    positions: [],
    history: [],
    portfolio: [],
    loading: true
  },

  onLoad() {
    this.refreshData();
    setInterval(() =&gt; this.refreshData(), 3000);
  },

  onPullDownRefresh() {
    this.refreshData();
    wx.stopPullDownRefresh();
  },

  async refreshData() {
    try {
      await Promise.all([
        this.fetchStatus(),
        this.fetchPositions(),
        this.fetchPortfolio(),
        this.fetchHistory()
      ]);
      this.setData({ loading: false });
    } catch (error) {
      console.error('刷新失败:', error);
      this.setData({ status: '连接失败' });
    }
  },

  async fetchStatus() {
    const res = await wx.request({
      url: `${API_BASE}/status`
    });
    
    if (res.statusCode === 200 &amp;&amp; res.data.success) {
      const data = res.data.data;
      let todayPnlClass = '';
      
      if (data.today_pnl &gt; 0) {
        todayPnlClass = 'pnl-positive';
      } else if (data.today_pnl &lt; 0) {
        todayPnlClass = 'pnl-negative';
      }
      
      this.setData({
        status: data.status,
        balance: '¥' + data.balance.toLocaleString(),
        todayPnl: '¥' + data.today_pnl.toLocaleString(),
        todayPnlClass: todayPnlClass,
        closedPnl: '¥' + data.closed_pnl.toLocaleString()
      });
    }
  },

  async fetchPositions() {
    const res = await wx.request({
      url: `${API_BASE}/positions`
    });
    
    if (res.statusCode === 200 &amp;&amp; res.data.success) {
      const positions = res.data.data.map(pos =&gt; ({
        ...pos,
        signalClass: this.getSignalClass(pos.signal),
        pnlClass: this.getPnlClass(pos.pnl)
      }));
      
      this.setData({
        positions: positions,
        totalPos: res.data.total_pos
      });
    }
  },

  async fetchPortfolio() {
    const res = await wx.request({
      url: `${API_BASE}/portfolio`
    });
    
    if (res.statusCode === 200 &amp;&amp; res.data.success) {
      this.setData({ portfolio: res.data.data });
    }
  },

  async fetchHistory() {
    const res = await wx.request({
      url: `${API_BASE}/history`,
      data: { size: 10 }
    });
    
    if (res.statusCode === 200 &amp;&amp; res.data.success) {
      this.setData({ history: res.data.data });
    }
  },

  getSignalClass(signal) {
    if (signal &amp;&amp; signal.includes('多头')) {
      return 'signal-long';
    }
    if (signal &amp;&amp; signal.includes('空头')) {
      return 'signal-short';
    }
    return 'signal-watch';
  },

  getPnlClass(pnl) {
    if (pnl &gt; 0) return 'pnl-positive';
    if (pnl &lt; 0) return 'pnl-negative';
    return 'pnl-zero';
  },

  copyAddress() {
    wx.setClipboardData({
      data: '请将策略部署到公网服务器',
      success: () =&gt; {
        wx.showToast({
          title: '已复制',
          icon: 'success'
        });
      }
    });
  }
});
