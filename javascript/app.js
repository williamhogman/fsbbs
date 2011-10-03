$script("http://cdnjs.cloudflare.com/ajax/libs/prototype/1.7.0.0/prototype.js","ptype");
$script("/s/templates.js","templates");
$script(["Markdown.Converter.js","Markdown.Sanitizer.js","Markdown.Editor.js"].map(function(v){
    return "/j/vendor/pagedown/"+v;
}),"markdown");
$script.ready(
    ["templates","ptype"],
    function(){
	console.log("loading fsbbs js");
	var api,remote,nearestAttribute,forumLinkClicked,history,addLinkEvents,updateInteractions,auth;
	api = window.fsbbs = {};	

	api.history = history = function(){
	    /** 
	     *  Interface to the HTML5 history api, if there is none we do nothing
	     *  Handles all onpopstates events
	     * 
	     *  Public memebers
	     *  pushThing(thing) - pushes a thing onto the history
	     */
	    
	    var r = {};
	    window.onpopstate = function(event){
		// call enter
		if(event.state != null)
		{
		    if(event.state.handle == "thing")
			renderThing(event.state.wrapped);
		    else if(event.state.handle == "first")
			loadThing(event.state.wrapped);

		}
	    };
	    var e = function(){},
	    push = (window.history.pushState ? window.history.pushState.bind(window.history) : e),
	    replace = (window.history.replaceState ? window.history.replaceState.bind(window.history) : e),

	    HistoryState = Class.create({
		initialize: function(o){
		    this.wrapped = o;
		    // get for how long this resource has been stored
		    this.stored = new Date();
		},
		enter: function(){
		    if(this.wrapped.onHistoryEnter)
		    {
			// call it and give it a chance to refresh
			this.wrapped.onHistoryEnter(this.stored);
		    }
		}
	    }),
	    ThingHistoryState = Class.create(HistoryState,
	    {
		initialize: function($super,o){
		    $super(o);
		    this.handle = "thing";
		},
		enter: function($super){
		    renderThing(this.wrapped);
		}
	    }),
	    FirstHistoryState = Class.create(HistoryState,
            {
		initialize: function($super,o)
		{
		    $super(o);
		    this.handle = "first";
		}
	    });

	    r.pushThing = function(thing){
		var url = "/t/"+thing.id+".html",
		state = new ThingHistoryState(thing),
		title  = thing.title || thing.name || thing.type || "thing";
		push(state,title,url);
	    };

	    (function(){
		firstId = $$("#things article")[0].readAttribute("data-id");
		replace(new FirstHistoryState(firstId),"","#");
	    })();

	    return r;
	}();

	api.remote = remote = function(){
	    var calls = 
		{
		    "get_thing": {url: "/api/get_thing.json", method: "GET"}
		};
	    var fns = $H();
	    $H(calls).each(function(p){
		// get our name and defaults
		var name= p[0],def = $H(p[1]);
		fns[name] = function(opt) {
		    // merge our args with the 
		    var o = def.merge(opt);
		    return new Ajax.Request(o.get('url'),o.toObject());
		};
	    });
	    return fns;
	}();

	api.auth = auth = function(){
	    var loggedin = false,
	    uid = null,
	    r = {};
	 
	    
	    r.setUser = function(userid){
		if(userid > 0)
		{
		    uid = userid;
		    loggedin = true;
		    console.log("logged in as",userid);
		} else {
		    console.warn("Tried to set user to non positive value");
		}
	    };
	    
	    r.isLoggedIn = function(){
		return loggedin;
	    };

	    r.setUser(window.initial_uid);
	    return r;
	}();

	var humanise = {};
	/* adapted from https://gist.github.com/colmjude  */
	humanise.date = (function() {
	    var measures = {
		second: 1,
		minute: 60,
		hour: 3600,
		day: 86400,
		week: 604800,
		month: 2592000,
		year: 31536000
	    }, chkMultiple = function(amount, type) {
		return (amount > 1) ? amount + " " + type + "s":"a " + type;
	    };

	    return function(thedate) {
		var dateStr, amount, denomination,
		current = new Date().getTime(),
		diff = (current - thedate.getTime()) / 1000; // work with seconds

		if(diff > measures.year) {
		    return  thedate.toLocaleString();
		} else if(diff > measures.month) {
			denomination = "month";
		} else if(diff > measures.week) {
			denomination = "week";
		} else if(diff > measures.day) {
			denomination = "day";
		} else if(diff > measures.hour) {
			denomination = "hour";
		} else if(diff > measures.minute) {
			denomination = "minute";
		} else {
			dateStr = "a few seconds ago";
			return dateStr;
		}
		amount = Math.round(diff/measures[denomination]);
		dateStr = chkMultiple(amount, denomination) + " ago";
		return dateStr;
	    };

	})();

	parseThing = function(thing){
	    if (thing.original_post && thing.original_post.pubdate)
	    {
		thing.original_post.pubdate = new Date(Date.parse(thing.original_post.pubdate));
		thing.original_post.pubdate_human = humanise.date(thing.original_post.pubdate);
		
	    } else if(thing.pubdate)
	    {
		thing.pubdate = new Date(Date.parse(thing.pubdate));
		thing.pubdate_human = humanise.date(thing.pubdate);
	    }

	    
	    if(thing.text){
		thing.text = md.toHTML(thing.text);
	    }
	    return thing;
	};



	/** walks the DOM untill it finds an attribute with the passed in name */
	nearestAttribute = function(elem,attr){
	    var res;
	    while(res == null) /* works b/c undefined == null && undefined !== null */
	    {
		res = elem.readAttribute(attr);
		up = elem.up();
		if(up == elem)
		    return null;
		elem = up;
	    }
	    return res;
	};

	updateInteractions = function(thing){
	    if(!auth.isLoggedIn())
	    {
		$('interactions').update("<p>You need to login in order to post</p>");
		return;
	    }
	    var frm;
	    if(thing.type == "category")
	    {
		frm = templates.form_new_topic.evaluate(thing);
		$("interactions").update(frm);
		md.addEditor("-newtopic");
		
	    } else if (thing.type == "topic")
	    {
		frm = templates.form_new_post.evaluate(thing);
		$("interactions").update(frm);
		md.addEditor("-newpost");
		
	    } else // maches none don't do 
	    {
		$("interactions").update("");
	    }

	};
	
	loadThing = function(tid){
	    var success = function(response){
		
		renderThing(response.responseJSON.thing);
		
	    };
	    remote.get_thing({"parameters": {"id": tid}, onSuccess: success});
	};
	
	renderThing = function(thing){
	    var rendered_contents;
	    rendered_contents = [templates.thing_start.evaluate(parseThing(thing))];
	    if(thing.type == "category")
	    {

		rendered_contents = rendered_contents.concat(thing.contents.map(function(sub){
		    return templates.category_topic.evaluate(parseThing(sub));
		}));

	    } else if (thing.type == "topic")
	    {
		rendered_contents.push(templates.topic_op.evaluate(parseThing(thing.original_post)));
		rendered_contents = rendered_contents.concat(thing.contents.map(function(sub){
		    return templates.topic_post.evaluate(parseThing(sub));
		}));

	    }
	    rendered_contents.push(templates.thing_end.evaluate(thing));
	    $('things').update(rendered_contents.join(""));
	    history.pushThing(thing);
	    addLinkEvents();
	    updateInteractions(thing);
	};

	forumLinkClicked = function(ev){
	    var id =  nearestAttribute(this,"data-id");
	    if(id != null)
	    {
		ev.stop();
		loadThing(id);

	    }
	};
	
	addLinkEvents = (function(){
    $$("article[data-id] a").each(function(item){
		item.observe("click",forumLinkClicked);
	    });
	});

	addLinkEvents();

	
	// markdown is scoped here
	var md = {};
	// yes, we are still inside our main namespace
	$script.ready("markdown",function(){
	    var converter = Markdown.getSanitizingConverter();
	    
	    md.addEditor = (function(idpostfix){
		if(!$("wmd-input"+idpostfix))
		{
		    return false;
		    console.warn(idpostfix, "missing");
		}
		    
		editor = new Markdown.Editor(converter,idpostfix);
		editor.run();
		return true;
	    });
            md.toHTML = function(text){
		return converter.makeHtml(text);
	    };
		      
	    
	    md.addEditor("-newtopic");
	    md.addEditor("-newpost");
	    console.log("new topics added");
	});

	
    });