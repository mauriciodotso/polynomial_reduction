from sympy import *
def simplify(ts):

	for i in range(len(ts)):
		for j in range(len(ts)):
			if i == j:
				continue
			if i > len(ts):
				continue
			if j > len(ts):
				continue
			t_left = ts[i]
			t_right = ts[j]

			if t_left.args[0].args[1] == t_right.args[0].args[1]:
				t_left_right = cancellit(t_left, t_right)
				if t_left_right is not None:
					ts[i] = t_left_right[0]
					ts[j] = t_right
					if t_right is None:
						del ts[j]

	return ts

def cancellit(t_left, t_right):
	t_left_upper = t_left.args[1][2].subs(b, (6*c - 3)/4).subs(c, 5)
	t_left_lower = t_left.args[1][1].subs(b, (6*c - 3)/4).subs(c, 5)
	t_right_upper = t_right.args[1][2].subs(b, (6*c - 3)/4).subs(c, 5)
	t_right_lower = t_right.args[1][1].subs(b, (6*c - 3)/4).subs(c, 5)

	if t_left_upper - t_right_upper < 0:
		temp_upper = t_left_upper
		temp_lower = t_left_lower
		t_left_upper = t_right_upper
		t_left_lower = t_right_lower
		t_right_upper = temp_upper
		t_right_lower = temp_lower

	if t_left_lower - t_right_upper < 0:
		lower_bound_subtraction = t_left_lower - t_right_lower
		if  lower_bound_subtraction > 0:
			'''
			t_left: |-----------------------------|
			t_right:   |-------------------|
			'''
			remaining_1 = Sum(Indexed('d', t_left.args[0].args[1]), (i, t_left.args[1][1], t_right.args[1][1] -1))
			remaining_2 = Sum(Indexed('d', t_left.args[0].args[1]), (i, t_right.args[1][2] + 1, t_left.args[1][2]))
			return remaining_1, remaining_2
		elif t_left_lower - t_right_lower == 0:
			'''
			t_left:    |-----------------------------|
			t_right:   |-------------------|
			'''
			remaining_1 = Sum(Indexed('d', t_left.args[0].args[1]), (i, t_right.args[1][2] + 1, t_left.args[1][2]))
			return remaining_1, None
		else:
			'''
			t_left:    |-----------------------------|
			t_right:|-------------------|
			'''
			remaining_1 = Sum(Indexed('d', t_left.args[0].args[1]), (i, t_right.args[1][1], t_left.args[1][1] - 1))
			remaining_2 = Sum(Indexed('d', t_left.args[0].args[1]), (i, t_right.args[1][2] + 1, t_left.args[1][2]))
			return remaining_1, remaining_2

def test_valid(t):
	temp_limit_inferior = t.args[1][1].subs(b, (6*c - 3)/4).subs(c, 5)
	temp_limit_superior = t.args[1][2].subs(b, (6*c - 3)/4).subs(c, 5)
	return temp_limit_superior > temp_limit_inferior

def reduction(m, a, b, c, z, levels):

	def bs_filter(t):
		temp_m = m.subs(b, (6*c - 3)/4).subs(c, 5)
		temp_limit = t.args[1][2].subs(b, (6*c - 3)/4).subs(c, 5)
		if temp_limit - temp_m > 0:
			return Sum(Indexed('d', t.args[0].args[1]), (i, t.args[1][1], m-1))
		else:
			return Sum(Indexed('d', t.args[0].args[1]), (i, t.args[1][1], t.args[1][2]))

	def as_filter(t):
		temp_m = m.subs(b, (6*c - 3)/4).subs(c, 5)
		temp_limit = t.args[1][1].subs(b, (6*c - 3)/4).subs(c, 5)
		if temp_limit - temp_m < 0:
			return Sum(Indexed('d', t.args[0].args[1]), (i, m, t.args[1][2]))
		else:
			return Sum(Indexed('d', t.args[0].args[1]), (i, t.args[1][1], t.args[1][2]))

	poly = Sum(Indexed('d', i), (i, 0, 2*m - 2))
	a0 = Sum(Indexed('d', i), (i, m, 2*m - 2))
	b0 = Sum(Indexed('d', i), (i, 0, m - 1))

	_reduction_step_a = lambda t: Sum(Indexed('d', t.args[0].args[1]+(m-a)), (i, m-(m-a), t.args[1][2]-(m-a)))
	_reduction_step_b = lambda t: Sum(Indexed('d', t.args[0].args[1]+(m-b)), (i, m-(m-b), t.args[1][2]-(m-b)))
	_reduction_step_c = lambda t: Sum(Indexed('d', t.args[0].args[1]+(m-c)), (i, m-(m-c), t.args[1][2]-(m-c)))
	_reduction_step_d = lambda t: Sum(Indexed('d', t.args[0].args[1]+(m-z)), (i, m-(m-z), t.args[1][2]-(m-z)))

	d_step= [a0]

	bs = [[b0]]
	as_ = [[a0]]
	d_steps = [[poly]]

	for ii in range(0, levels):
		step_a = map(_reduction_step_a, d_step)
		step_b = map(_reduction_step_b, d_step)
		step_c = map(_reduction_step_c, d_step)
		step_d = map(_reduction_step_d, d_step)
		
		d_step = list(step_a) + list(step_b) + list(step_c) + list(step_d)
		d_step = list(filter(test_valid, d_step))
		d_step = simplify(d_step)
		d_step = list(filter(test_valid, d_step))

		bs = bs + [list(map(bs_filter, d_step))]
		as_ = as_ + [list(map(as_filter, d_step))]
		d_steps = d_steps + [ d_step]

	new_bs = []
	for step in bs:
		new_step = []
		for sum in step:
			if test_valid(sum):
				new_step.append(sum)
		new_bs = new_bs + [new_step]

	new_as = []
	for step in as_:
		new_step = []
		for sum in step:
			if test_valid(sum):
				new_step.append(sum)
		new_as = new_as + [new_step]


	return new_bs, new_as, d_steps
	

def pprint_latex(bs, as_, ds, b_sum):
	for i in range(0, len(bs)):
		print("step d{}:".format(i))
		print("\\begin{equation}")
		print("\\begin{split}")
		print("D_{{{}}} = ".format(i), end="")
		s = 0
		for b in ds[i]:
			s = s + 1
			if s % 2 == 0:
				print("\\sum_{{i={}}}^{{{}}} d_{{{}}}x^i".format(b.args[1][1], b.args[1][2], b.args[0].args[1]), end="")
				print("\\\\")
			else:
				print("\\sum_{{i={}}}^{{{}}} d_{{{}}}x^i + ".format(b.args[1][1], b.args[1][2], b.args[0].args[1]), end="")
		print("\\end{split}")
		print("\\end{equation}")

		print("step b{}:".format(i))
		print("\\begin{equation}")
		print("\\begin{split}")
		print("B_{{{}}} = ".format(i), end="")
		s = 0
		for b in bs[i]:
			s = s + 1
			if s % 2 == 0:
				print("\\sum_{{i={}}}^{{{}}} d_{{{}}}x^i".format(b.args[1][1], b.args[1][2], b.args[0].args[1]), end="")
				print("\\\\")
			else:
				print("\\sum_{{i={}}}^{{{}}} d_{{{}}}x^i + ".format(b.args[1][1], b.args[1][2], b.args[0].args[1]), end="")
		print("\\end{split}")
		print("\\end{equation}")


		print("step a{}:".format(i))
		print("\\begin{equation}")
		print("\\begin{split}")
		print("A_{{{}}} = ".format(i), end="")
		s = 0
		for b in as_[i]:
			s = s + 1
			if s % 2 == 0:
				print("\\sum_{{i={}}}^{{{}}} d_{{{}}}x^i".format(b.args[1][1], b.args[1][2], b.args[0].args[1]), end="")
				print("\\\\")
			else:
				print("\\sum_{{i={}}}^{{{}}} d_{{{}}}x^i + ".format(b.args[1][1], b.args[1][2], b.args[0].args[1]), end="")
		print("\\end{split}")
		print("\\end{equation}")

	print("Sum of B's:")
	print("\\begin{equation}")
	print("\\begin{split}")
	print("B_0 + B_1 + B_2 + B_3 + B_4 + B_5 + B_6 = ", end="")
	s = 0
	for b in b_sum:
		s = s + 1
		if s % 2 == 0:
			print("\\sum_{{i={}}}^{{{}}} d_{{{}}}x^i".format(b.args[1][1], b.args[1][2], b.args[0].args[1]), end="")
			print(" + \\\\")
		else:
			print("\\sum_{{i={}}}^{{{}}} d_{{{}}}x^i + ".format(b.args[1][1], b.args[1][2], b.args[0].args[1]), end="")
	print("\\end{split}")
	print("\\end{equation}")


if __name__ == "__main__":
	i = symbols('i')
	c, b = symbols("c b", integer=True, positive=True)
	d = Integer(0)
	a = 2 * c
	m = b + c

	init_printing(use_unicode=True)
	bs, as_, ds = reduction(m, a, b, c, d, 6)

	b_sum = []
	for j in range(len(bs)):
		b_sum = b_sum + bs[j]

	b_sum = simplify(b_sum)
	b_sum = list(filter(test_valid, b_sum))

	pprint_latex(bs, as_, ds, b_sum)
