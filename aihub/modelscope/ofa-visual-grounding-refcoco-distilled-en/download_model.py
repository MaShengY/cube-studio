

from modelscope.pipelines import pipeline
from modelscope.utils.constant import Tasks

p = pipeline('visual-grounding', 'damo/ofa_visual-grounding_refcoco_distilled_en')