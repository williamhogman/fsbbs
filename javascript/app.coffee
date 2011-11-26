$script "http://cdnjs.cloudflare.com/ajax/libs/prototype/1.7.0.0/prototype.js","ptype"
$script "/s/templates.js", "templates"

@$vendor = (ns,lib) ->
        $script "/j/vendor/"+ns+"/"+lib+".js", lib;

$script.ready ["templates","ptype"], ->
        console.log "loading fsbbs"

        api = window.fsbbs = {}

        api.history = history = (->
                r = {}
                window.onpopstate = (ev) ->
                        if(event.state != null)
                                if event.state.handle == "thing"
                                        renderThing(event.state.wrapped)
                                else if event.state.handle == "first"
                                        loadThing(event.state.wrapped)

                e = -> undefined
                if window.history?
                        push = window.history.pushState.bind(window.history)
                        replace = window.history.replaceState.bind(window.history)
                else
                        push = e
                        replace = e

                class HistoryState
                        constructor: (o) ->
                                @wrapped = o
                                @stored = new Date()
                        enter: ->
                                if @wrapped.onHistoryEnter?
                                    @wrapped.onHistoryEnter(this.stored)
                class ThingHistoryState extends HistoryState
                        constructor: (o) ->
                                super o
                                @handle = "thing"
                        enter: -> renderThing(@wrapped)

                class FirstHistoryState extends HistoryState
                        constructor: (o) ->
                                super o
                                @handle = "first"
                r.pushThing = (thing) ->
                        url = "/t/"+thing.id+".html"
                        state = new ThingHistoryState(thing)
                        title = thing.title || thing.name || thing.type || "thing"
                        push(state,title,url)

                (->
                        art = $$("#things article")
                        if art.length > 0
                                firstId =art[0].readAttribute("data-id")
                        else
                                firstId = 1
                        replace new FirstHistoryState(firstId),"","#"
                )()

                return r
                )()
        api.remote = remote = (->
                calls = $H(
                        get_thing:
                                url: "/api/get_thing.json"
                                method: "GET"
                        logout:
                                url: "/api/logout.json"
                                method: "POST"
                        login:
                                url: "/api/login.json"
                                method: "POST"
                        register:
                                url: "/api/register.json"
                                method: "POST"
                );
                fns = $H();
                $H(calls).each (p)->
                        name = p[0]
                        def = $H(p[1])
                        fns[name] = (opt) ->
                                o = def.merge(opt)
                                new Ajax.Request(o.get("url"),o.toObject())
                return fns
                )()

        api.validation = validation = (->
                r = {}
                validators =
                        notEmpty: (elem) ->
                                if elem.getValue().trim() == ""
                                        elem.up().addClassName "error"
                                        return false
                                return true
                class Form
                        constructor: (form,options) ->
                                @form = form
                                @options = options
                        validate: ->
                                form = @form
                                @options.all (o) ->
                                        field = form[o[0]]
                                        validators = o[1]
                                        validators.all (o) ->
                                                if o.isString()
                                                        return validators[o](field)
                                                else if o.isFunction()
                                                        return o(field)
                                                else
                                                        throw "validator must be string or function"






                r.Form = form;
                return r
                )()

        api.modal = modal = (->
                r = {}
                modals = []

                class ModalWindow
                        constructor: (id) ->
                                @element = new Element("div",class: "modalWindow", id: id)
                        show: ->
                                # this works because the setCallbacks
                                # (and therefore.defer) are queued up
                                # after oneanother.
                                @element.addClassName.bind(this.element).defer("show")
                                if cb? then cb.defer()

                        insert: (elem) -> @element.insert(elem)
                        hideAndDelete: ->
                                @element.removeClassName("show")
                                @element.element.remove.delay(1)
                        addIntoDOM:
                                $(document.body).insert(@element)


                r.ModalWindow = ModalWindow
                return r
                )()
        api.auth = (->
                loggedin = false
                uid = null
                username = null
                r = {}

                r.ui = (->
                        e = {}
                        loginbar = $$(".loginbar")[0]

                        e.update = ->
                                if loggedin
                                        msg = templates.status_user.evaluate(username: username)
                                        btn_logout = new Element("a",class: "button logout-btn",href: "#")
                                        btn_logout.update("Logout")
                                        btn_logout.observe("click",-> r.doLogout())
                                        loginbar.update(msg).insert(btn_login).insert(btn_reg)
                                else
                                        msg = templates.status_guest.evaluate(username: username)
                                        btn_login = new Element("a",class: "button login-btn",href: "#")
                                        btn_login.update("Login")
                                        btn_login.observe("click",showLoginModal)

                                        btn_reg = new Element("a",class: "button register-btn",href: "#")
                                        btn_reg.update("Register")
                                        btn_reg.observe("click",showRegisterModal)
                                        loginbar.update(msg).insert(btn_login).insert(btn_reg)


                        showLoginModal = ->
                                modalBox = new modal.ModalWindow("modal-login")
                                form = new Element("form")
                                form.insert(templates.modal_login_title.evaluate())
                                form.insert(templates.modal_login.evaluate())
                                modalBox.insert(form)
                                modalBox.addIntoDOM()
                                modalBox.show()

                                form.observe "submit", (ev) ->
                                        ev.stop()
                                        username =  @username.getValue().trim()
                                        password = @password.getValue()

                                        passed = true

                                        infobox = @down(".infobox")

                                        @descendants().each (v) ->
                                                if v.hasClassName "error" then v.removeClassName "error"
                                        if username == ""
                                                passed = false
                                                @username.up().addClassName "error"
                                                infobox.update "<p>Please fill in all the fields</p>"

                                        if password == ""
                                                passed = false
                                                @password.up().addClassName "error"
                                                infobox.update "<p>Please fill in all the fields</p>"

                                        if not passed then return

                                        remote.login(
                                                parameters:
                                                        username: username
                                                        password: password
                                                onSuccess: (resp) ->
                                                        res = resp.responseJSON
                                                        if res.status == "success"
                                                                r.setUser(res.uid,username)
                                                                modalBox.hideAndDelete()
                                                        else if res.status == "invalid"
                                                                r.setUser(res.uid)
                                                        else
                                                                @password.clear().up().addClassName("error")
                                                                infobox.update "<p>Incorrect username or password</p>"
                                                onFailure: (resp) -> infobox.update "<p>Something went wrong...</p>"
                                                )

                        showRegisterModal = ->
                                modalBox = new modal.ModalWindow("modal-register")
                                form = new Element("form")
                                form.insert(templates.modal_register_title.evaluate())
                                form.insert(templates.modal_register.evaluate())
                                modalBox.insert(form)
                                modalBox.addIntoDOM()
                                modalBox.show()
                                form.obserbe "submit",->
                                        ev.stop()
                                        username = @username.getValue().trim()
                                        password = @password.getValue()
                                        passed = true
                                        infobox @down(".infobox")
                                        @descendants().each (v) ->
                                                if v.hasClassName "error" then v.removeClassName "error"
                                        if username == ""
                                                passed = false
                                                @username.up().addClassName "error"
                                                infobox.update "<p>Please fill in all the fields</p>"
                                        if password == ""
                                                passed = false
                                                @password.up().addClassName "error"
                                                infobox.update "<p>Please fill in all the fields</p>"

                                        if not passed then return
                                        infobox.update ""
                                        remote.register(
                                                parameters:
                                                        username: username
                                                        password: password
                                                onSuccess: (resp) ->
                                                        res = resp.reponseJSON
                                                        if res.status == "success"
                                                                r.setUser res.uid,res.username
                                                                modalBox.hideAndDelete()
                                                        else if res.status == "invalid"
                                                                r.setUser(res.uid)
                                                                modalBox.hideAndDelete()
                                                        else
                                                                infobox.update "<p>Username taken</p>"
                                                onFailure: (resp) -> infobox.update "<p>Something went wrong...</p>"
                                        )
                        return e
                       )()

                r.doLogout = (cb) ->
                        remote.logout onSuccess: ->
                                loggedIn = false
                                uid = null
                                if cb? then cb()
                                r.ui.update()


                r.setUser = (userid,uname) ->
                        if userid < 1 then return console.warn("tried to set user to invalid UID")

                        username = uname
                        uid = userid
                        loggedin = true

                r.isLoggedIn = -> loggedin

                r.setUser(window.initial_uid)

                r # return r
                )()


                humanise = {}

                humanise.date = (->
                        measures = (
                                second: 1
                                minute: 60
                                hour: 3600
                		day: 86400
                		week: 604800
                		month: 2592000
                		year: 31536000
                                )

                        chkMultiple = (amount,type) ->
                                if amount > 1
                                        amount+" "+type+"s"
                                else
                                        "a "+type
                        (thedate) ->
                                current = new Date().getTime()
                                diff = current - thedate.getTime() /1000

                                if diff > measures.year then return thedate.toLocaleString()
                                else if diff > measures.month then denom = "month"
                                else if diff > measures.week then denom = "week"
                                else if diff > measures.day then denom = "day"
                                else if diff > measures.hour then denom = "hour"
                                else if diff > measures.minute then denom = "minute"
                                else return "a few seconds ago"

                                amount = Math.round diff/measures[denom]
                                return chkMultuple(amount,denom) + " ago"
                                )()

                parseThing = (thing) ->
                        # crates extra properties on a downloaded thing
                        # and performs conversions to markdown

                        if thing.original_post? and thing.original_post.pubdate?
                                op = thing.original_post
                                op.pubdate = new Date(Date.parse(op.pubdate))
                                op.pubdate_human = humanise.date op.pubdate
                        else if thing.pubdate?
                                thing.pubdate = new Date(Date.parse(thing.pubdate))
                                thing.pubdate_human = humanise.date thing.pubdate

                        if thing.text then thing.text = md.toHTML(thing.text)

                        return thing

                # walks the DOM untill it finds an attribute with the passed in name
                nearestAttribute = (elem,attr) ->
                        res = null
                        while res == null
                                res = elem.readAttribute(attr)
                                up = elem.up()
                                if up == elem
                                        return null
                                elem = up
                        return res

                updateInteractions = (thing) ->
                        #
                        # Updates the interactions (posting etc) ui
                        # according to the current login state and
                        # page (being a category or a topic)
                        elem = $("interations")
                        if not auth.isLoggedIn()
                                elem.update "<p>You need to login in order to post</p>"
                                return

                        if thing.type == "category"
                                frm = templates.form_new_topic.evaluate(thing)
                                elem.update(frm)
                                md.addEditor("-newtopic")
                        else if thing.type == "topic"
                                frm = templates.form_new_post.evaluate(thing)
                                elem.update(frm)
                                md.addEditor("-newpost")
                        else elem.update("")

                loadThing = (tid) ->
                        # loads a thing from the server
                        remote.get_thing(
                                parameters:
                                        id: tid
                                onSuccess: -> renderThing(response.responseJSON.thing)
                                )
                renderThing = (thing) ->
                        # renders the passed in thing
                        rendered = [templates.thing_start.evaluate(parseThing(thing))]
                        if thing.type == "category"
                                rendered = rendered.concat(thing.contents.map( (sub) ->
                                        templates.category_topic.evaluate(parseThing(sub))
                                ))
                        else if thing.type == "topic"
                                rendered.push(templates.topic_op.evaluate(parseThing(thing.original_post)))
                                rendered.concat(thing.contents.map( (sub) ->
                                        templates.topic_post.evaluate(parseThing(sub))
                                ))
                        rendered.push(templates.thing_end.evaluate(thing))
                        $("things").update(rendered_contents.join(""))
                        history.pushThing(thing)
                        addLinkEvents()
                        updateInterations()

                forumLinkCliked = (ev) ->
                        id = nearestAttribute(this,"data-id")
                        if id?
                                ev.stop()
                                loadThing(id)
                addLinkEvents = ->
                        $$("article[data-id] a").each (item) ->
                                item.observe "click", forumLinkClicked
                addLinkEvents()

                md = {}
                $script.ready "markdown", ->
                        converter = Markdown.getSanitizingConverter()
                        md.addEditor = (postfix) ->
                                if not $("wmd-input-"+postfix)?
                                        console.warn(postfix,"missing")
                                        return false
                                editor = new Markdown.Editor(converter,postfix)
                                editor.run()
                                return true

                        md.toHTML = (text) -> converter.makeHtml(text)

                        md.addEditor("-newtopic")
                        md.addEditor("-newpost")


                document.observe "dom:loaded", -> setTimeout(auth.ui.update,3)























