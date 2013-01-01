var Bar,
  __bind = function(fn, me){ return function(){ return fn.apply(me, arguments); }; };

Bar = (function() {

  Bar.name = 'Bar';

  function Bar() {
    this.initialize = __bind(this.initialize, this);

  }

  Bar.prototype.initialize = function() {
    return this.bob = 'test';
  };

  return Bar;

})();
var Foo,
  __bind = function(fn, me){ return function(){ return fn.apply(me, arguments); }; };

Foo = (function() {

  Foo.name = 'Foo';

  function Foo() {
    this.initialize = __bind(this.initialize, this);

  }

  Foo.prototype.initialize = function(f) {
    return this.bar = new Bar();
  };

  return Foo;

})();