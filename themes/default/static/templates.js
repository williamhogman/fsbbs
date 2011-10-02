$script.ready("ptype",function()
{
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

});
