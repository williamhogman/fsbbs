$script("http://cdnjs.cloudflare.com/ajax/libs/prototype/1.7.0.0/prototype.js","ptype");
$script("/s/templates.js","templates");
$script(["Markdown.Converter.js","Markdown.Sanitizer.js","Markdown.Editor.js"].map(function(v){
    return "/j/vendor/pagedown/"+v;
}),"markdown");
$script.ready(
    ["templates","ptype"],
    function(){
	console.log("loading fsbbs js");
	var api,remote,nearestAttribute,forumLinkClicked,history,addLinkEvents,updateInteractions,auth,modal;
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
	    /**
	     * Exposes methods on the server in a faux-rpc way
	     */
	    var calls = 
		{
		    "get_thing": {url: "/api/get_thing.json", method: "GET"},
		    "logout": {url: "/api/logout.json", method: "POST"},
		    "login": {url: "/api/login.json", method: "POST"},
		    "register": {url: "/api/register.json", method: "POST" }
		},
	    fns = $H();
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

	api.validation = validation = function(){
	    	/**
		 * Validation api, handles form validation
		 */
	    var r = {},
	    validators = {"notEmpty": function(elem){
			      if (elem.getValue().trim() == "")
				  {
				      elem.up().addClassName("error");
				      return false;
				  }
			      return true;
			  }};
	    /**
	     * Class for wrapping a form with validation features
	     */
	    r.Form = Class.create
	    ({
		 initialize: function(form,options){
		     this.form = form;
		     this.options = options;
		    },
		 validate: function(){
		     var form = this.form;
		     return this.options.all(function(o){
					  var field =  form[o[0]],
					   validators = o[1];
					   
					   return validators.all(function(o){
							      if(o.isString())
							       {
								   return validators[o](field);
							       } else if(o.isFunction()) {
								   return o(field);
							       } else {
								   throw "validator must be string or function";
							       }
							  });
					   

				       });

		 }
	    });

	    return r;
	}();
	api.modal = modal = function(){
	    /**
	     * API for creating modal windows
	     */
	    var r = {},
	    modals = [];
	    r.ModalWindow = Class.create
	    ({
		 initialize: function(id){
		     this.element = new Element("div",{'class': 'modalWindow', 'id': id});
		 },
		 show: function(cb){
		     this.element.addClassName.bind(this.element).defer("show");
		     if(cb){
			 // this defer will be called after the addClassName call because of defer is just
			 // queuing up things on the UI loop
			 cb.defer();
		     }
			 
		 },
		 insert: function(elem){
		     this.element.insert(elem);
		 },
		 hideAndDelete: function(){
		     this.element.removeClassName("show");
		     this.element.remove.delay(1);
		 },
		 addIntoDOM: function(){
		     $(document.body).insert(this.element);
		 }
	     });
	    return r;
	}();
	api.auth = auth = function(){
	    var loggedin = false,
	    uid = null,
	    username = null,
	    r = {};

	    r.ui = function(){
		var e={},
		loginbar = $$(".loginbar")[0];
		e.update = function(){
		    var msg;
		    if(loggedin) {
			msg = templates.status_user.evaluate({username: username});
			
			// yeah reverse hungarian notation; 
			var btn_logout = new Element("a",{'class': 'button logout-btn', href: "#"});
			btn_logout.update("Logout");
			btn_logout.observe("click",function(){
					       r.doLogout();
					   });

			loginbar.update(msg).insert(btn_logout);

		    } else {
			msg = templates.status_guest.evaluate({username: username});
			var btn_login = new Element("a",{'class': 'button login-btn', href: "#"});
			btn_login.update("Login");
			btn_login.observe("click",showLoginModal);
			
			var btn_reg = new Element("a",{'class': 'button register-btn', href: "#"});
			btn_reg.update("Register");
			btn_reg.observe("click",showRegisterModal);

			loginbar.update(msg).insert(btn_login).insert(btn_reg);
		    }
		};


		function showLoginModal()
		{
		    //var modalBox = new Element("div",{'class': 'modalWindow','id': 'modal-login' }),
		    var modalBox = new modal.ModalWindow('modal-login'),
		    form = new Element("form");
		    form.insert(templates.modal_login_title.evaluate());
		    form.insert(templates.modal_login.evaluate());

		    modalBox.insert(form);
		    modalBox.addIntoDOM();

		    modalBox.show();

		    form.observe("submit",function(ev){
				     ev.stop();

				     var t = this,
				     username = t.username.getValue().trim(),
				     password = t.password.getValue(),
				     passedValidation = true,
				     infobox = t.down(".infobox");
				     
				     
				     
				     t.descendants().each(function(v){
							      // dom writes are expensive as hell
							      if(v.hasClassName("error"))
								  v.removeClassName("error");			
							   });
				     
				     if(username == "")
				     {
					 passedValidation = false;
					 t.username.up().addClassName("error");
					 infobox.update("<p>Please fill in all the fields</p>");
				     }
				     
				     if(password == "")
				     {
					 passedValidation = false;
					 t.password.up().addClassName("error");
					 infobox.update("<p>Please fill in all the fields</p>");
				     }
				     
				     if(!passedValidation)
				     {
					 return;
				     }
				     infobox.update("");
				     
				     remote.login({parameters: {username: username,password:password},
						  onSuccess: function(resp){
						      var res = resp.responseJSON;
						      if(res.status =="success")
							  {
							      r.setUser(res.uid,username);
							      modalBox.hideAndDelete();
							  } else if (res.status=="invalid") {
							      r.setUser(res.uid);
							      modalBox.hideAndDelete();
							  } else {
							      t.password.clear().up().addClassName("error");
							      infobox.update("<p>Incorrect username or password</p>");
							  }
						      
						      e.update();
						  },
						  onFailure: function(resp){
						      infobox.update("<p>Something went wrong...</p>");
						  }});
				     
				 });
		}

		function showRegisterModal()
		{
		    var modalBox = new modal.ModalWindow("modal-register");
		    form = new Element("form");
		    form.insert(templates.modal_register_title.evaluate());
		    form.insert(templates.modal_register.evaluate());
		    
		    modalBox.insert(form);
		    
		    modalBox.addIntoDOM();
		    
		    modalBox.show();
		    form.observe("submit",function(ev){
				     ev.stop();
				     var t = this,
				     username = t.username.getValue().trim(),
				     password = t.password.getValue(),
				     passedValidation = true,
				     infobox = t.down(".infobox");
				     
				     
				     
				     t.descendants().each(function(v){
							      // dom writes are expensive as hell
							      if(v.hasClassName("error"))
								  v.removeClassName("error");			
							   });
				     
				     if(username == "")
				     {
					 passedValidation = false;
					 t.username.up().addClassName("error");
					 infobox.update("<p>Please fill in all the fields</p>");
				     }
				     
				     if(password == "")
				     {
					 passedValidation = false;
					 t.password.up().addClassName("error");
					 infobox.update("<p>Please fill in all the fields</p>");
				     }
				     
				     if(!passedValidation)
				     {
					 return;
				     }
				     infobox.update("");

				     remote.register({parameters: {username: username,password:password},
						  onSuccess: function(resp){
						      var res = resp.responseJSON;
						      if(res.status =="success")
							  {
							      r.setUser(res.uid,res.username);
							      modalBox.hideAndDelete();
							  } else if (res.status=="invalid") {
							      r.setUser(res.uid);
							      modalBox.hideAndDelete();
							  } else {
							      infobox.update("<p>Username taken</p>");
							  }
						      
						      e.update();
						  },
						  onFailure: function(resp){
						      infobox.update("<p>Something went wrong...</p>");
						  }});

				     
				 });

		}
		
		return e;
            }();
	    
	    r.doLogout = function(cb){
		remote.logout({onSuccess: function(){
				   loggedin = false;
				   uid = null;
				   if(cb) cb();
				   r.ui.update();
			       }});
	    };
	    
	    r.setUser = function(userid,uname){
		if(userid > 0)
		{
		    username = uname;
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
	    /**
	     * Handles the rendering of a thing from the datastore
	     */
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
	
	document.observe("dom:loaded",function(){
			     setTimeout(auth.ui.update,3);
			 });
    });