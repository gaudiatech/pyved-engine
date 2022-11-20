from katagames_engine.foundation.defs import CircularBuffer


cb = CircularBuffer(3)
print(str(cb))
print("Empty: {}".format(cb.is_empty()))
print("Full: {}".format(cb.is_full()))
print()

cb.enqueue("one")
cb.enqueue("two")
cb.enqueue("three")
cb.enqueue("four")
print(str(cb))
print("Empty: {}".format(cb.is_empty()))
print("Full: {}".format(cb.is_full()))
print()

print(cb.dequeue())

print('front?', cb.front())
print(str(cb))
print(cb.get_size())
print("Empty: {}".format(cb.is_empty()))
print("Full: {}".format(cb.is_full()))
print()

cb.enqueue("five")
cb.enqueue("six")
print(str(cb))
print('front? ', cb.front())
print(cb.get_size())
print("Empty: {}".format(cb.is_empty()))
print("Full: {}".format(cb.is_full()))
print()

print(cb.dequeue())
print(cb.dequeue())
print(cb.dequeue())
print(str(cb))
print(cb.get_size())
print("Empty: {}".format(cb.is_empty()))
print("Full: {}".format(cb.is_full()))
