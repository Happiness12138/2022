Page({
  data: {
    user_gamenum:'',
    user_keyword:'',
    user_icnum:'',
    user_name:'',
    user_face:'',
    isAuth: false,
    src: ''
  },
  // 身份证号码输入值130481200005282111
  onLoad() {
    // 前三个方法和const常量都是camera.js里定义的
    const _this = this
    wx.getSetting({
      success: res => {
        if (res.authSetting['scope.camera']) {
          // 用户已经授权
          _this.setData({
            isAuth: true
          })
        } else {
          // 用户还没有授权，向用户发起授权请求
          wx.authorize({
            scope: 'scope.camera',
            success() { // 用户同意授权
              _this.setData({
                isAuth: true
              })
            },
            fail() { // 用户不同意授权
              _this.openSetting().then(res => {
                _this.setData({
                  isAuth: true
                })
              })
            }
          })
        }
      },
      fail: res => {
        console.log('获取用户授权信息失败')
      }
      // 请求
    })
  },
  // 打开授权设置界面
  openSetting() {
    const _this = this
    let promise = new Promise((resolve, reject) => {
      wx.showModal({
        title: '授权',
        content: '请先授权获取摄像头权限',
        success(res) {
          if (res.confirm) {
            wx.openSetting({
              success(res) {
                if (res.authSetting['scope.camera']) { // 用户打开了授权开关
                  resolve(true)
                } else { // 用户没有打开授权开关， 继续打开设置页面
                  _this.openSetting().then(res => {
                    resolve(true)
                  })
                }
              },
              fail(res) {
                console.log(res)
              }
            })
          } else if (res.cancel) {
            _this.openSetting().then(res => {
              resolve(true)
            })
          }
        }
      })
    })
    return promise;
  },

  takePhoto() {
    const that = this;
    const ctx = wx.createCameraContext()
    ctx.takePhoto({
      quality: 'high',
      success: (res) => {
        console.log("拍照");
        this.setData({
          src: res.tempImagePath
        })
 
        console.log('开始保存')
        wx.setStorage({
          key: 'key1',
          data: this.data.src,
          success: function (res) {
            console.log('异步保存成功')
          }
        }),
          //获取缓存
          wx.getStorage({
            key: 'key1',
            success: function (res) {
              console.log(res.data)
            }
          })
          wx.getImageInfo({
            src: this.data.src,
            success: function (res) {
              var path = res.path;
              //保存图片到本地
              wx.saveImageToPhotosAlbum({
                filePath: path,
                success: function () {
                  wx.showToast({
                    title: '保存成功'
                  })
                },
                fail: function (res) {
                  wx.showToast({
                    title: '保存失败',
                    icon: 'none'
                  })
                }
              })
            }
          })
          
      
      }
    })
  },
  chooseImg(){
    var that = this;
    wx.chooseImage({
      success: res => {
      wx.getFileSystemManager().readFile({
          filePath: res.tempFilePaths[0], //选择图片返回的相对路径
          encoding: 'base64', //编码格式
          success: res => { //成功的回调
            this.data.user_face = res.data
            this.data.user_face.replace("+","%2B")
            console.log(this.data.user_face)
          }
        })
      }
    }) 
  },
  // ---------------------------------------------------------------------------------------
  // 游戏账号
  bindGameNumInput: function(e) {
    this.setData({
      user_gamenum: e.detail.value
    })
  },
  // 密码输入检测
  bindKeywordInput: function(e) {
    this.setData({
      user_keyword: e.detail.value
    })
  },
  bindICNumInput(e) {
    this.setData({
      user_icnum: e.detail.value
    })
  },
  bindNameInput:function(e){
    this.setData({
      user_name:e.detail.value
    })
  },
  // 身份证号码输入值130481200005282111
  // 130481199905282111
  loginBtnAction() {
    // console.log(this.data.user_gamenum)
    var that = this;
    if(this.data.user_gamenum.length == 0 || this.data.user_keyword.length == 0 || this.data.user_icnum.length == 0 || this.data.user_name.length == 0 || this.data.user_face.length == 0){
      wx.showModal({
        title: '提示',
        content:'请完善个人信息并选中一张人脸图像在进行实名认证！'
      })
    }
    else{
      wx.request({
        url: 'http://127.0.0.1:5000/index/',
        method:'GET',
        header: {      
          'content-type': 'application/json' // 默认值
        }, 
        data:{
          uid:this.data.user_gamenum,
          keyword:this.data.user_keyword,
          id: this.data.user_icnum,
          name: this.data.user_name,
          face: this.data.user_face
        },
        // 身份证号码输入值130481200005282111
        // 130481199905282111
        success: function (res) {
          console.log("成功了！！！")
          console.log(res)
          var isuid = res.data.isuid;
          var iskeyword = res.data.iskeyword;
          var isid = res.data.isid;
          var isidone = res.data.isidone;
          var isfacerecognition = res.data.isfacerecognition;
          var isfacematching = res.data.isfacematching;
          var isAdult = res.data.isAdult;
          console.log(isuid)
          console.log("又成功了！！！")
          // 老用户
          if(isuid){ 
            // 密码
            if(iskeyword){
              if(isid == 1){
                if(isfacerecognition){
                  if(isfacematching){
                    if(isAdult == 0){
                      wx.showModal({
                        title: '提示',
                        content:'未成年禁止在现在玩！'
                      })
                    }
                    else if(isAdult == 1){
                      wx.showModal({
                        title: '提示',
                        content:'未成年现在可以玩！'
                      })
                    }
                    else if(isAdult == 2){
                      wx.showModal({
                        title: '提示',
                        content:'成年人可以玩！'
                      })
                    }
                    wx.showModal({
                      title: '提示',
                      content:'人脸匹配成功，正在检测是否未成年！'
                    })
                  }
                  else{
                    wx.showModal({
                      title: '提示',
                      content:'人脸匹配失败！'
                    })
                  }
                  wx.showModal({
                    title: '提示',
                    content:'人脸识别成功！正在进行人脸匹配！'
                  })
                }
                else{
                  wx.showModal({
                    title: '提示',
                    content:'人脸识别失败！'
                  })
                }
              }
              else if(isid == 2){
                wx.showModal({
                  title: '提示',
                  content:'绑定身份证不一致！'
                })
              }
              wx.showModal({
                title: '提示',
                content:'您已成年，请登录！'
              })
              wx.showModal({
                title: '提示',
                content:'您未成年！现在不可以登录，每周六周日的九点到十点可以登录！'
              })
            }
            else{
              wx.showModal({
                title: '提示',
                content:'您未成年！现在不可以登录，每周六周日的九点到十点可以登录！'
              })
            }
          }
          // 新用户
          else{
            if(isid == 0){
              if(isidone){
                if(isfacerecognition){
                  if(isAdult == 0){
                    wx.showModal({
                      title: '提示',
                      content:'未成年禁止在现在玩！'
                    })
                  }
                  else if(isAdult == 1){
                    wx.showModal({
                      title: '提示',
                      content:'未成年现在可以玩！'
                    })
                  }
                  else if(isAdult == 2){
                    wx.showModal({
                      title: '提示',
                      content:'成年人可以玩！'
                    })
                  }
                  wx.showModal({
                    title: '提示',
                    content:'人脸识别成功！系统正在检测是否未成年！'
                  })
                }
                else{
                  wx.showModal({
                    title: '提示',
                    content:'人脸识别失败！'
                  })
                }
                wx.showModal({
                  title: '提示',
                  content:'绑定身份证成功！'
                })
              }
              else{
                wx.showModal({
                  title: '提示',
                  content:'该身份证已绑定其他账号，绑定身份证失败！'
                })
              }
              wx.showModal({
                title: '提示',
                content:'正在为您绑定该身份证！'
              })
            }
            wx.showModal({
              title: '提示',
              content:'账号不存在，已为您注册此账号！'
            })
          }
          }
        })
    }
    
    }
})
