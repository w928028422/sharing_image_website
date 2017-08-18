/**
 * Created by Administrator on 2017/8/17 0017.
 */
var comment = $(function () {
    var oExports = {
        initialize: fInitializeComment,
        encode: fEncode
    };
    oExports.initialize();
});

function fInitializeComment() {
    var that = this;
    var sImageId = document.getElementsByClassName('image-id');
    var oCmtIpt = document.getElementsByClassName('jsCmt');
    var oListDv = document.getElementsByClassName('js-discuss-list');
    var oCommentsLength = document.getElementsByClassName('comments_length');

    // 点击添加评论
    var bSubmit = false;
    $('.jsSubmit').on('click', function () {
        var index = Number(this.id) - 1;
        //console.log(sImageId, oCmtIpt, oListDv);
        var sCmt = $.trim(oCmtIpt[index].value);
        // 评论为空不能提交
        if (!sCmt) {
            return alert('评论不能为空');
        }
        // 上一个提交没结束之前，不再提交新的评论
        if (bSubmit) {
            return;
        }
        bSubmit = true;
        $.ajax({
            url: '/addcomment/',
            type: 'post',
            dataType: 'json',
            data: {image_id: sImageId[index].value, content: sCmt}
        }).done(function (oResult) {
            if (oResult.code !== 0) {
                return alert(oResult.msg || '提交失败，请重试');
            }
            // 清空输入框
            oCmtIpt[index].value = '';
            // 渲染新的评论
            var sHtml = [
                '<li>',
                '<!-- <a class=" icon-remove" title="删除评论"></a> -->',
                '<a class="_4zhc5 _iqaka" title="zjuyxy" href="/profile/', oResult.user_id, '" >',
                fEncode(oResult.username), '</a>',
                '<span><span>', fEncode(sCmt), '</span> </span>',
                '</li>'
            ].join('');

            oListDv[index].prepend($(sHtml).get(0));
            oCommentsLength[index].innerHTML = Number(oCommentsLength[index].innerHTML) + 1;
        }).fail(function (oResult) {
            alert(oResult.msg || '提交失败，请重试');
        }).always(function () {
            bSubmit = false;
        });
    });

    $('.load-more').on('click', function(){
        var inde = Number(this.name) - 1;
        var dataSize = 5;
        var uList = document.getElementsByClassName('js-discuss-list')[inde];
        var start_index = uList.getElementsByTagName('li').length;
        var current_comments = document.getElementsByClassName('comments_length')[inde];
        var imageId = document.getElementsByClassName('image-id')[inde].value;
        if (current_comments === start_index){
            alert('没有更多评论了!');
            return;
        }
        $.ajax({
            url: '/loadmorecomment/',
            type: 'post',
            dataType: 'json',
            data: {image_id:imageId, data_size:dataSize, start:start_index}
        }).done(function (oResult) {
            if (oResult.code !== 0)
                alert(oResult.msg || oResult.msg || '提交失败，请重试');
            $.each(oResult.comments , function (nIndex, oComment) {
                var sHtml = [
                    '<li>',
                    '<a class="_4zhc5 _iqaka" title="zjuyxy" href="/profile/', oComment.user_id, '" >',
                    fEncode(oComment.username), '</a>',
                    '<span><span>', fEncode(oComment.content), '</span> </span>',
                    '</li>'
                ].join('');
                uList.append($(sHtml).get(0));
            });
        }).fail(function (oResult) {
            alert(oResult.msg || '提交失败，请重试');
        });
    });
}

function fEncode(sStr, bDecode) {
        var aReplace =["&#39;", "'", "&quot;", '"', "&nbsp;", " ", "&gt;", ">", "&lt;", "<", "&amp;", "&", "&yen;", "¥"];
        !bDecode && aReplace.reverse();
        for (var i = 0, l = aReplace.length; i < l; i += 2) {
             sStr = sStr.replace(new RegExp(aReplace[i],'g'), aReplace[i+1]);
        }
        return sStr;
    }


