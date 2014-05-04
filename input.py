# @method move
# @type setter
# @param integer 32 dist
# @param bool 8 forward

# @method rotate
# @type setter
# @param integer 32 angle
# @param bool 8 isAbs

# @method goto
# @type setter
# @param integer 32 x
# @param integer 32 y
# @param integer 32 delta_max

# @method getPosition
# @type getter
# @param integer 32 x
# @param integer 32 y
# @param integer 32 angle

-# @method setOdo
-# @type setter
-# @param integer 32 x
-# @param integer 32 y
-# @param integer 32 angle
-# @param integer 8 flag
-
-# @method setDistKpKd
-# @type setter
-# @param integer 32 kp
-# @param integer 32 kd
-
-# @method getLinKpKd
-# @type getter
-# @param integer 32 kp
-# @param integer 32 kd
-
-# @method setRotKpKd
-# @type setter
-# @param integer 32 kp
-# @param integer 32 kd
-
-# @method getRotKpKd
-# @type getter
-# @param integer 32 kp
-# @param integer 32 kd
-
-# @method getUltrasounds
-# @type getter
-# @param integer 8 kp
-# @param integer 32 dist
-
-# @method getJumper
-# @type getter
-# @param bool dist
-
-# @method getStatus
-# @type getter
-# @param bool bfr
-# @param bool bfl
-# @param bool bbr
-# @param bool bbl
-# @param bool cmdhack