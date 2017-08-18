/**
 * Created by Administrator on 2017/8/16 0016.
 */
$(function () {
    var oExports = {
        initialize: fInitialize,
        // 渲染更多数据
        renderMore: fRenderMore,
        // 请求数据
        requestData: fRequestData,
        // 简单的模板替换
        tpl: fTpl
    };
    // 初始化页面脚本
    oExports.initialize();

    function fInitialize() {
        var that = this;
        // 常用元素
        that.listEl = $('div.js-image-list');
        // 初始化数据
        that.page = 1;
        that.pageSize = 10;
        that.indexCount = that.pageSize;
        that.listHasNext = true;
        // 绑定事件
        that.loadMore = $('.js-load-more');
        that.loadMore.on('click', function (oEvent) {
            var oEl = $(oEvent.currentTarget);
            var sAttName = 'data-load';
            // 正在请求数据中，忽略点击事件
            if (oEl.attr(sAttName) === '1') {
                return;
            }
            // 增加标记，避免请求过程中的频繁点击
            oEl.attr(sAttName, '1');
            that.renderMore(function () {
                // 取消点击标记位，可以进行下一次加载
                oEl.removeAttr(sAttName);
                // 没有数据隐藏加载更多按钮
                !that.listHasNext && oEl.hide();
            });
        });
    }

    function fRenderMore(fCb) {
        var that = this;
        // 没有更多数据，不处理
        if (!that.listHasNext) {
            return;
        }
        that.requestData({
            page: that.page + 1,
            pageSize: that.pageSize,
            call: function (oResult) {
                // 是否有更多数据
                that.listHasNext = !!oResult.has_next && (oResult.images || []).length > 0;
                // 更新当前页面
                that.page++;
                // 渲染数据
                var sHtml = '';
                var oComments = oResult.comments;
                $.each(oResult.images, function (nIndex, oImage) {
                    that.indexCount++;
                    sHtml += that.tpl([
                        '<article class="mod">',
                        '<header class="mod-hd">',
                        '<time class="time">#{create_date}</time>',
                        '<a href="/profile/#{user_id}" class="avatar">',
                        '<img src="#{head_url}">',
                        '</a>',
                        '<div class="profile-info">',
                        '<a title="#{username}" href="/profile/#{user_id}"></a>',
                        '</div>',
                        '</header>',
                        '<div class="mod-bd">',
                        '<div class="img-box">',
                        '<a href="/image/#{id}">',
                        '<img src="#{url}">',
                        '</a>',
                        '</div>',
                        '</div>',
                        '<a class="load-more" href="javascript:void(0)" name="' +that.indexCount+ '">',
                        '<span>全部 </span><span class="comments_length">#{comments_count}</span>',
                        '<span> 条评论</span>',
                        '</a>',
                        '<div class="mod-ft">',
                        '<ul class="discuss-list js-discuss-list" onload="">'
                    ].join(''), oImage);
                    $.each(oComments[nIndex], function (index, oComment) {
                        if (index > 2){
                            return false;
                        }
                        var oData = oComment;
                        var str = [
                            '<li>',
                            '<a class="_4zhc5 _iqaka" title="zjuyxy" href="/profile/{comment_user_id}" data-reactid=".0.1.0.0.0.2.1.2:$comment-17856951190001917.1">{comment_username}</a>',
                            '<span>',
                            '<span>{content}</span>',
                            '</span>',
                            '</li>'
                        ].join('');
                        if (oData) {
                            var pattern = $.trim(str).match(/{(.*?)}/g);
                            sHtml += $.trim(str).replace(/{(.*?)}/g, function (sStr, sName) {
                                return oData[sName] === undefined || oData[sName] === null ? '' : oData[sName];
                            });
                        }

                    });


                    sHtml += '</ul><section class="discuss-edit">\
                                    <a class="icon-heart-empty"></a>\
                                    <input placeholder="添加评论..." class="jsCmt" type="text">\
                                    <button class="more-info jsSubmit" id="'+
                                    that.indexCount
                        +'">更多选项</button>\
                                    <input type="hidden" value="' +
                                        oImage.id
                                    + '" class="image-id">\
                              </section>\
                            </div>\
                        </article>';
                });
                sHtml && that.listEl.append(sHtml);
                that.listHasNext && that.listEl.append(that.loadMore);
                fInitializeComment();
            },
            error: function () {
                alert('出现错误，请稍后重试');
            },
            always: fCb
        });
    }

    function fRequestData(oConf) {
        var that = this;
        var sUrl = '/index/images/' + oConf.page + '/' + oConf.pageSize + '/';
        $.ajax({url: sUrl, dataType: 'json'}).done(oConf.call).fail(oConf.error).always(oConf.always);
    }

    function fTpl(sTpl, oData) {
        var that = this;
        sTpl = $.trim(sTpl);
        return sTpl.replace(/#{(.*?)}/g, function (sStr, sName) {
            return oData[sName] === undefined || oData[sName] === null ? '' : oData[sName];
        });
    }

});