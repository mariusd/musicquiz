//MooTools More, <http://mootools.net/more>. Copyright (c) 2006-2009 Aaron Newton <http://clientcide.com/>, Valerio Proietti <http://mad4milk.net> & the MooTools team <http://mootools.net/developers>, MIT Style License.

MooTools.More={version:"1.2.4.4",build:"6f6057dc645fdb7547689183b2311063bd653ddf"};Element.implement({measure:function(e){var g=function(h){return !!(!h||h.offsetHeight||h.offsetWidth);
};if(g(this)){return e.apply(this);}var d=this.getParent(),f=[],b=[];while(!g(d)&&d!=document.body){b.push(d.expose());d=d.getParent();}var c=this.expose();
var a=e.apply(this);c();b.each(function(h){h();});return a;},expose:function(){if(this.getStyle("display")!="none"){return $empty;}var a=this.style.cssText;
this.setStyles({display:"block",position:"absolute",visibility:"hidden"});return function(){this.style.cssText=a;}.bind(this);},getDimensions:function(a){a=$merge({computeSize:false},a);
var f={};var d=function(g,e){return(e.computeSize)?g.getComputedSize(e):g.getSize();};var b=this.getParent("body");if(b&&this.getStyle("display")=="none"){f=this.measure(function(){return d(this,a);
});}else{if(b){try{f=d(this,a);}catch(c){}}else{f={x:0,y:0};}}return $chk(f.x)?$extend(f,{width:f.x,height:f.y}):$extend(f,{x:f.width,y:f.height});},getComputedSize:function(a){a=$merge({styles:["padding","border"],plains:{height:["top","bottom"],width:["left","right"]},mode:"both"},a);
var c={width:0,height:0};switch(a.mode){case"vertical":delete c.width;delete a.plains.width;break;case"horizontal":delete c.height;delete a.plains.height;
break;}var b=[];$each(a.plains,function(g,f){g.each(function(h){a.styles.each(function(i){b.push((i=="border")?i+"-"+h+"-width":i+"-"+h);});});});var e={};
b.each(function(f){e[f]=this.getComputedStyle(f);},this);var d=[];$each(a.plains,function(g,f){var h=f.capitalize();c["total"+h]=c["computed"+h]=0;g.each(function(i){c["computed"+i.capitalize()]=0;
b.each(function(k,j){if(k.test(i)){e[k]=e[k].toInt()||0;c["total"+h]=c["total"+h]+e[k];c["computed"+i.capitalize()]=c["computed"+i.capitalize()]+e[k];}if(k.test(i)&&f!=k&&(k.test("border")||k.test("padding"))&&!d.contains(k)){d.push(k);
c["computed"+h]=c["computed"+h]-e[k];}});});});["Width","Height"].each(function(g){var f=g.toLowerCase();if(!$chk(c[f])){return;}c[f]=c[f]+this["offset"+g]+c["computed"+g];
c["total"+g]=c[f]+c["total"+g];delete c["computed"+g];},this);return $extend(e,c);}});Element.implement({isDisplayed:function(){return this.getStyle("display")!="none";
},isVisible:function(){var a=this.offsetWidth,b=this.offsetHeight;return(a==0&&b==0)?false:(a>0&&b>0)?true:this.isDisplayed();},toggle:function(){return this[this.isDisplayed()?"hide":"show"]();
},hide:function(){var b;try{b=this.getStyle("display");}catch(a){}return this.store("originalDisplay",b||"").setStyle("display","none");},show:function(a){a=a||this.retrieve("originalDisplay")||"block";
return this.setStyle("display",(a=="none")?"block":a);},swapClass:function(a,b){return this.removeClass(a).addClass(b);}});Fx.Reveal=new Class({Extends:Fx.Morph,options:{link:"cancel",styles:["padding","border","margin"],transitionOpacity:!Browser.Engine.trident4,mode:"vertical",display:"block",hideInputs:Browser.Engine.trident?"select, input, textarea, object, embed":false},dissolve:function(){try{if(!this.hiding&&!this.showing){if(this.element.getStyle("display")!="none"){this.hiding=true;
this.showing=false;this.hidden=true;this.cssText=this.element.style.cssText;var d=this.element.getComputedSize({styles:this.options.styles,mode:this.options.mode});
this.element.setStyle("display",this.options.display);if(this.options.transitionOpacity){d.opacity=1;}var b={};$each(d,function(f,e){b[e]=[f,0];},this);
this.element.setStyle("overflow","hidden");var a=this.options.hideInputs?this.element.getElements(this.options.hideInputs):null;this.$chain.unshift(function(){if(this.hidden){this.hiding=false;
$each(d,function(f,e){d[e]=f;},this);this.element.style.cssText=this.cssText;this.element.setStyle("display","none");if(a){a.setStyle("visibility","visible");
}}this.fireEvent("hide",this.element);this.callChain();}.bind(this));if(a){a.setStyle("visibility","hidden");}this.start(b);}else{this.callChain.delay(10,this);
this.fireEvent("complete",this.element);this.fireEvent("hide",this.element);}}else{if(this.options.link=="chain"){this.chain(this.dissolve.bind(this));
}else{if(this.options.link=="cancel"&&!this.hiding){this.cancel();this.dissolve();}}}}catch(c){this.hiding=false;this.element.setStyle("display","none");
this.callChain.delay(10,this);this.fireEvent("complete",this.element);this.fireEvent("hide",this.element);}return this;},reveal:function(){try{if(!this.showing&&!this.hiding){if(this.element.getStyle("display")=="none"||this.element.getStyle("visiblity")=="hidden"||this.element.getStyle("opacity")==0){this.showing=true;
this.hiding=this.hidden=false;var d;this.cssText=this.element.style.cssText;this.element.measure(function(){d=this.element.getComputedSize({styles:this.options.styles,mode:this.options.mode});
}.bind(this));$each(d,function(f,e){d[e]=f;});if($chk(this.options.heightOverride)){d.height=this.options.heightOverride.toInt();}if($chk(this.options.widthOverride)){d.width=this.options.widthOverride.toInt();
}if(this.options.transitionOpacity){this.element.setStyle("opacity",0);d.opacity=1;}var b={height:0,display:this.options.display};$each(d,function(f,e){b[e]=0;
});this.element.setStyles($merge(b,{overflow:"hidden"}));var a=this.options.hideInputs?this.element.getElements(this.options.hideInputs):null;if(a){a.setStyle("visibility","hidden");
}this.start(d);this.$chain.unshift(function(){this.element.style.cssText=this.cssText;this.element.setStyle("display",this.options.display);if(!this.hidden){this.showing=false;
}if(a){a.setStyle("visibility","visible");}this.callChain();this.fireEvent("show",this.element);}.bind(this));}else{this.callChain();this.fireEvent("complete",this.element);
this.fireEvent("show",this.element);}}else{if(this.options.link=="chain"){this.chain(this.reveal.bind(this));}else{if(this.options.link=="cancel"&&!this.showing){this.cancel();
this.reveal();}}}}catch(c){this.element.setStyles({display:this.options.display,visiblity:"visible",opacity:1});this.showing=false;this.callChain.delay(10,this);
this.fireEvent("complete",this.element);this.fireEvent("show",this.element);}return this;},toggle:function(){if(this.element.getStyle("display")=="none"||this.element.getStyle("visiblity")=="hidden"||this.element.getStyle("opacity")==0){this.reveal();
}else{this.dissolve();}return this;},cancel:function(){this.parent.apply(this,arguments);this.element.style.cssText=this.cssText;this.hidding=false;this.showing=false;
}});Element.Properties.reveal={set:function(a){var b=this.retrieve("reveal");if(b){b.cancel();}return this.eliminate("reveal").store("reveal:options",a);
},get:function(a){if(a||!this.retrieve("reveal")){if(a||!this.retrieve("reveal:options")){this.set("reveal",a);}this.store("reveal",new Fx.Reveal(this,this.retrieve("reveal:options")));
}return this.retrieve("reveal");}};Element.Properties.dissolve=Element.Properties.reveal;Element.implement({reveal:function(a){this.get("reveal",a).reveal();
return this;},dissolve:function(a){this.get("reveal",a).dissolve();return this;},nix:function(){var a=Array.link(arguments,{destroy:Boolean.type,options:Object.type});
this.get("reveal",a.options).dissolve().chain(function(){this[a.destroy?"destroy":"dispose"]();}.bind(this));return this;},wink:function(){var b=Array.link(arguments,{duration:Number.type,options:Object.type});
var a=this.get("reveal",b.options);a.reveal().chain(function(){(function(){a.dissolve();}).delay(b.duration||2000);});}});