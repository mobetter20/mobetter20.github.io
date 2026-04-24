---
id: checkout-standard
trigger: always
type: linear
---

## script

::clerk
[irasshaimase]。
::

::clerk
[otsugi]でお待《ま》ちのお客様《きゃくさま》、どうぞ。
::

::action
player_places_items
::

::clerk
[goukei] {{basket_total}}円《えん》になります。
::

::player-choice
a: はい、[onegai]します | polite
b: お願《ねが》いします | casual-polite
::

::action
payment_exchange
::

::clerk
{{payment_amount}}円《えん》[oazukari]します。
::

::clerk
{{change_amount}}円《えん》の[okaeshi]です。[receipt]のご利用《りよう》は?
::

::player-choice
a: [onegai]します | wants_receipt
b: [daijoubu]です | declines_receipt
::

::clerk-branch[wants_receipt]
はい、[receipt]です。
::

::clerk-branch[declines_receipt]
かしこまりました。
::

::clerk
[arigatou]ございました。
::

::exit
The doors slide open. You are outside the konbini. Briefly.
::
