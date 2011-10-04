$script.ready("ptype",function(){
    var _ = window.templates = {},
    t = function(a){return new Template(a);};


    _.category_topic = t(
	'<article data-id="#{id}"><a href="/t/#{id}.html"><h3>#{title}</h3></a>'+
	    'Topic created by <a href="/u/#{original_post.poster_uid}">'+
	    '#{original_post.poster_name}</a>&nbsp;'+
	    '<time timedate="#{original_post.pubdate}">'+
	    '#{original_post.pubdate_human}</time>'+
	    '<div class="clearfix"></div></article>'
    );
    
    _.thing_start = t(
	'<article class="thing thing-#{type}" data-id="#{id}"><header>'+
	    '<a rel="self"><h2>#{title}</h2></a>'+
	    '</header>'
    );
    
    _.topic_post = t(
	'<article data-id="#{id}"><header>'+
	    'Posted by <a data-id="3" href="/u/#{poster_uid}.html">#{poster_name}</a>&nbsp;'+
	    '<time datetime="#{pubdate}">#{pubdate_human}</time>'+
	    '</header>'+ 
	    '<div>#{text}</div>'+
	    '</article>'
    );

    _.topic_op = t(
	'<p>Topic created by <a data-id="3" href="/u/3.html">william</a>&nbsp;'+
	    '<time datetime="#{pubdate}">#{pubdate_human}</time></p>'+
	    '<div class="op">#{text}</div>'
    );

    _.thing_end =  t(
	"</article>"
    );

    _.form_new_topic = t(
	'<form action="/new_topic" method="post">'+
	    "<legend>Create topic</legend>"+
	    '<input type="hidden" name="tid" value="#{id}" />'+
	    '<div class="input">'+
	    '<label for="title">Title</label>'+
	    '<input class="largeinput" type="text" name="title" />'+
	    '</div>'+
	    '<div class="input wmd-panel">'+
	    '<label for="text">Text</label>'+
	    '<div id="wmd-button-bar-newtopic"></div>'+
	    '<textarea class="wmd-input" id="wmd-input-newtopic" name="text"></textarea>'+
	    '</div>'+
	    '<div id="wmd-preview-newtopic" class="wmd-panel wmd-preview"></div>'+
	    '<div class="actions">'+
	    '<input type="submit" value="Post" />'+
	    '</div>'+
	    '</form>'
    );

    _.form_new_post = t(
	'<form action="/new_post" method="post">'+
	    '<legend>Reply to this topic</legend>'+
	    '<input type="hidden" value="#{id}" name="tid" />'+
	    '<div class="input wmd-panel">'+
	    '<label for="text">Text</label>'+
	    '<div id="wmd-button-bar-newpost"></div>'+
	    '<textarea class="wmd-input" name="text" id="wmd-input-newpost"></textarea>'+
	    '</div>'+
	    '<div id="wmd-preview-newpost" class="wmd-preview">'+
	    '</div>'+
	    '<div class="actions">'+
	    '<input type="submit" value="Post" />'+
	    '</div>'+
	    '</form>'
    );

    _.status_guest = t(
	'<span>You are not logged in.</span>'
    );

    _.status_user = t(
	"<span>Welcome back #{username}</span>"
    );

    _.modal_login_title = t(
	"<h3>Login</h3>"+
	'<p>Login in with your username and password</p>'
    );
    _.modal_login = t(
	'<div class="input"><label for="username">Username</label><input type="text" placeholder="Username" name="username" /></div>'+
	    '<div class="input"><label for="password">Password</label> <input type="password" placeholder="Password" name="password" /></div>'+
	    '<div class="actions"><input type="submit" value="Login" /></div>'
    );

});
