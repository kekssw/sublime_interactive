
def rectangle(data, min_width=-1, center=False, left_padding=0, right_padding=-1):
    lines = data.split('\n')
    widest_length = max([len(x) for x in lines])
    widest_length += 0 if left_padding < 0 else left_padding
    widest_length += 0 if right_padding < 0 else right_padding
    widest_length = widest_length if widest_length > min_width else min_width

    for i, line in enumerate(lines):
        line_length = len(line)
        remaining = widest_length - line_length
        # If both have no indent, we just center line
        if left_padding == right_padding == -1:
            left_spaces = remaining // 2
        # If left has no indent but right does
        elif left_padding == -1:
            # left is whatever is left after the fix right indent
            left_spaces = (remaining - right_padding)
            # if this is a centered line
            if center:
                # left is half of what is left after right has it's indent
                left_spaces = left_spaces // 2
        # else left has a fixed indent
        else:
            left_spaces = left_padding
            # if center
            if center:
                # left is it's indent + half remainder
                left_spaces = left_padding + (remaining - left_padding) // 2

        right_spaces = remaining - left_spaces
        lines[i] = '%s%s%s' % (' ' * left_spaces, line, ' ' * right_spaces)

    data = '\n'.join(lines)
    if len(lines) > 1:
        data += ' '
    return data
