This is the final release of v0.13.0 for vLLM Ascend. Please follow the [official doc](https://docs.vllm.ai/projects/ascend/en/v0.13.0/) to get started.

### Highlights

**Model Support**
- **Qwen3-Next**: Full support for Qwen3-Next series including 80B-A3B-Instruct with full graph mode, MTP, quantization (W8A8), NZ optimization, and chunked prefill. Fixed multiple accuracy and stability issues. [#3450](https://github.com/vllm-project/vllm-ascend/pull/3450) [#3572](https://github.com/vllm-project/vllm-ascend/pull/3572) [#3428](https://github.com/vllm-project/vllm-ascend/pull/3428) [#3918](https://github.com/vllm-project/vllm-ascend/pull/3918) [#4058](https://github.com/vllm-project/vllm-ascend/pull/4058) [#4245](https://github.com/vllm-project/vllm-ascend/pull/4245) [#4070](https://github.com/vllm-project/vllm-ascend/pull/4070) [#4477](https://github.com/vllm-project/vllm-ascend/pull/4477) [#4770](https://github.com/vllm-project/vllm-ascend/pull/4770)
- **DeepSeek-R1 & DeepSeek-V3.2**: Added support for DeepSeek-R1 multimodal capabilities and improved DeepSeek-V3.2 with MTP support, performance optimizations, and async scheduling enhancements. [#3631](https://github.com/vllm-project/vllm-ascend/pull/3631) [#3900](https://github.com/vllm-project/vllm-ascend/pull/3900) [#3908](https://github.com/vllm-project/vllm-ascend/pull/3908) [#4191](https://github.com/vllm-project/vllm-ascend/pull/4191) [#4805](https://github.com/vllm-project/vllm-ascend/pull/4805)
- **InternVL**: Added support for InternVL models with comprehensive e2e tests and accuracy evaluation. [#3796](https://github.com/vllm-project/vllm-ascend/pull/3796) [#3964](https://github.com/vllm-project/vllm-ascend/pull/3964)
- **LongCat-Flash**: Added support for LongCat-Flash model. [#3833](https://github.com/vllm-project/vllm-ascend/pull/3833)
- **minimax_m2**: Added support for minimax_m2 model. [#5624](https://github.com/vllm-project/vllm-ascend/pull/5624)
- **Whisper & Cross-Attention**: Added support for cross-attention and Whisper models. [#5592](https://github.com/vllm-project/vllm-ascend/pull/5592)
- **Pooling Models**: Added support for pooling models with PCP adaptation and fixed multiple pooling-related bugs. [#3122](https://github.com/vllm-project/vllm-ascend/pull/3122) [#4143](https://github.com/vllm-project/vllm-ascend/pull/4143) [#6056](https://github.com/vllm-project/vllm-ascend/pull/6056) [#6057](https://github.com/vllm-project/vllm-ascend/pull/6057) [#6146](https://github.com/vllm-project/vllm-ascend/pull/6146)
- **PanguUltraMoE**: Added support for PanguUltraMoE model. [#4615](https://github.com/vllm-project/vllm-ascend/pull/4615)

**Core Features**
- **Context Parallel (PCP/DCP)**: [Experimental] Added comprehensive support for Prefill Context Parallel (PCP) and Decode Context Parallel (DCP) with ACLGraph, MTP, chunked prefill, MLAPO, and Mooncake connector integration. This is an experimental feature - feedback welcome. [#3260](https://github.com/vllm-project/vllm-ascend/pull/3260) [#3731](https://github.com/vllm-project/vllm-ascend/pull/3731) [#3801](https://github.com/vllm-project/vllm-ascend/pull/3801) [#3980](https://github.com/vllm-project/vllm-ascend/pull/3980) [#4066](https://github.com/vllm-project/vllm-ascend/pull/4066) [#4098](https://github.com/vllm-project/vllm-ascend/pull/4098) [#4183](https://github.com/vllm-project/vllm-ascend/pull/4183) [#5672](https://github.com/vllm-project/vllm-ascend/pull/5672)
- **Full Graph Mode (ACLGraph)**: Enhanced full graph mode with GQA support, memory optimizations, unified logic between ACLGraph and Torchair, and improved stability. [#3560](https://github.com/vllm-project/vllm-ascend/pull/3560) [#3970](https://github.com/vllm-project/vllm-ascend/pull/3970) [#3812](https://github.com/vllm-project/vllm-ascend/pull/3812) [#3879](https://github.com/vllm-project/vllm-ascend/pull/3879) [#3888](https://github.com/vllm-project/vllm-ascend/pull/3888) [#3894](https://github.com/vllm-project/vllm-ascend/pull/3894) [#5118](https://github.com/vllm-project/vllm-ascend/pull/5118)
- **Multi-Token Prediction (MTP)**: Significantly improved MTP support with chunked prefill for DeepSeek, quantization support, full graph mode, PCP/DCP integration, and async scheduling. MTP now works in most cases and is recommended for use. [#2711](https://github.com/vllm-project/vllm-ascend/pull/2711) [#2713](https://github.com/vllm-project/vllm-ascend/pull/2713) [#3620](https://github.com/vllm-project/vllm-ascend/pull/3620) [#3845](https://github.com/vllm-project/vllm-ascend/pull/3845) [#3910](https://github.com/vllm-project/vllm-ascend/pull/3910) [#3915](https://github.com/vllm-project/vllm-ascend/pull/3915) [#4102](https://github.com/vllm-project/vllm-ascend/pull/4102) [#4111](https://github.com/vllm-project/vllm-ascend/pull/4111) [#4770](https://github.com/vllm-project/vllm-ascend/pull/4770) [#5477](https://github.com/vllm-project/vllm-ascend/pull/5477)
- **Eagle Speculative Decoding**: Eagle spec decode now works with full graph mode and is more stable. [#5118](https://github.com/vllm-project/vllm-ascend/pull/5118) [#4893](https://github.com/vllm-project/vllm-ascend/pull/4893) [#5804](https://github.com/vllm-project/vllm-ascend/pull/5804)
- **PD Disaggregation**: Set ADXL engine as default backend for disaggregated prefill with improved performance and stability. Added support for KV NZ feature for DeepSeek decode node. [#3761](https://github.com/vllm-project/vllm-ascend/pull/3761) [#3950](https://github.com/vllm-project/vllm-ascend/pull/3950) [#5008](https://github.com/vllm-project/vllm-ascend/pull/5008) [#3072](https://github.com/vllm-project/vllm-ascend/pull/3072)
- **KV Pool & Mooncake**: Enhanced KV pool with Mooncake connector support for PCP/DCP, multiple input suffixes, and improved performance of Layerwise Connector. [#3690](https://github.com/vllm-project/vllm-ascend/pull/3690) [#3752](https://github.com/vllm-project/vllm-ascend/pull/3752) [#3849](https://github.com/vllm-project/vllm-ascend/pull/3849) [#4183](https://github.com/vllm-project/vllm-ascend/pull/4183) [#5303](https://github.com/vllm-project/vllm-ascend/pull/5303)
- **EPLB (Elastic Prefill Load Balancing)**: EPLB is now more stable with many bug fixes. Mix placement now works. [#6086](https://github.com/vllm-project/vllm-ascend/pull/6086)
- **Full Decode Only Mode**: Added support for Qwen3-Next and DeepSeekv32 in full_decode_only mode with bug fixes. [#3949](https://github.com/vllm-project/vllm-ascend/pull/3949) [#3986](https://github.com/vllm-project/vllm-ascend/pull/3986) [#3763](https://github.com/vllm-project/vllm-ascend/pull/3763)
- **Model Runner V2**: Added basic support for Model Runner V2, the next generation of vLLM. It will be used by default in future releases. [#5210](https://github.com/vllm-project/vllm-ascend/pull/5210)

### Features

- **W8A16 Quantization**: Added new W8A16 quantization method support. [#4541](https://github.com/vllm-project/vllm-ascend/pull/4541)
- **UCM Connector**: Added UCMConnector for KV Cache Offloading. [#4411](https://github.com/vllm-project/vllm-ascend/pull/4411)
- **Batch Invariant**: Implemented basic framework for batch invariant feature. [#5517](https://github.com/vllm-project/vllm-ascend/pull/5517)
- **Sampling**: Enhanced sampling with async_scheduler and disable_padded_drafter_batch support in Eagle. [#4893](https://github.com/vllm-project/vllm-ascend/pull/4893)

### Hardware and Operator Support

- **Custom Operators**: Added multiple custom operators including:
  - Fused matmul/reduce-scatter kernel [#3693](https://github.com/vllm-project/vllm-ascend/pull/3693)
  - mrope fusion op [#3708](https://github.com/vllm-project/vllm-ascend/pull/3708)
  - Triton chunk_gated_delta_rule ops for Qwen3-Next [#4070](https://github.com/vllm-project/vllm-ascend/pull/4070)
  - l2norm triton kernel [#4595](https://github.com/vllm-project/vllm-ascend/pull/4595)
  - RejectSampler, MoeInitRoutingCustom, DispatchFFNCombine custom ops
- **Operator Fusion**: Added AddRmsnormQuant fusion pattern with SP support and inductor fusion for quantization. [#5077](https://github.com/vllm-project/vllm-ascend/pull/5077) [#4168](https://github.com/vllm-project/vllm-ascend/pull/4168)
- **MLA/SFA**: Refactored SFA into MLA architecture for better maintainability. [#3769](https://github.com/vllm-project/vllm-ascend/pull/3769)
- **FIA Operator**: Adapted to npu_fused_infer_attention_score with flash decoding function. To optimize performance in small batch size scenarios, this attention operator is now available. Please refer to item 22 in [FAQs](https://docs.vllm.ai/projects/ascend/en/latest/faqs.html) to enable it. [#4025](https://github.com/vllm-project/vllm-ascend/pull/4025)
- **CANN 8.5 Support**: Removed CP redundant variables after FIA operator enables for CANN 8.5. [#6039](https://github.com/vllm-project/vllm-ascend/pull/6039)

### Performance

Many custom ops and triton kernels were added in this release to speed up model performance:

- **DeepSeek Performance**: Improved performance for DeepSeek V3.2 by eliminating HD synchronization in async scheduling and optimizing memory usage for MTP. [#4805](https://github.com/vllm-project/vllm-ascend/pull/4805) [#2713](https://github.com/vllm-project/vllm-ascend/pull/2713)
- **Qwen3-Next Performance**: Improved performance with Triton ops and optimizations. [#5664](https://github.com/vllm-project/vllm-ascend/pull/5664) [#5984](https://github.com/vllm-project/vllm-ascend/pull/5984) [#5765](https://github.com/vllm-project/vllm-ascend/pull/5765)
- **FlashComm**: Enhanced FlashComm v2 optimization with o_shared linear and communication domain fixes. [#3232](https://github.com/vllm-project/vllm-ascend/pull/3232) [#4188](https://github.com/vllm-project/vllm-ascend/pull/4188) [#4458](https://github.com/vllm-project/vllm-ascend/pull/4458) [#5848](https://github.com/vllm-project/vllm-ascend/pull/5848)
- **MoE Optimization**: Optimized all2allv for MoE models and enhanced all-reduce skipping logic. [#3738](https://github.com/vllm-project/vllm-ascend/pull/3738) [#5329](https://github.com/vllm-project/vllm-ascend/pull/5329)
- **Attention Optimization**: Moved attention update stream out of loop, converted BSND to TND format for long sequence optimization, and removed transpose step after attention switching to transpose_batchmatmul. [#3848](https://github.com/vllm-project/vllm-ascend/pull/3848) [#3778](https://github.com/vllm-project/vllm-ascend/pull/3778) [#5390](https://github.com/vllm-project/vllm-ascend/pull/5390)
- **Quantization Performance**: Moved quantization before allgather in Allgather EP. [#3420](https://github.com/vllm-project/vllm-ascend/pull/3420)
- **Layerwise Connector**: Improved performance of Layerwise Connector. [#5303](https://github.com/vllm-project/vllm-ascend/pull/5303)
- **Prefix Cache**: Improved performance of prefix cache features. [#4022](https://github.com/vllm-project/vllm-ascend/pull/4022)
- **Async Scheduling**: Fixed async copy and eliminated hangs in async scheduling. [#4113](https://github.com/vllm-project/vllm-ascend/pull/4113) [#4233](https://github.com/vllm-project/vllm-ascend/pull/4233)
- **Memory Operations**: Removed redundant D2H operations and deleted redundant operations in model_runner. [#4063](https://github.com/vllm-project/vllm-ascend/pull/4063) [#3677](https://github.com/vllm-project/vllm-ascend/pull/3677)
- **Rope Embedding**: Optimized rope embedding with triton kernel for huge performance gain. [#5918](https://github.com/vllm-project/vllm-ascend/pull/5918)
- **Sampling**: Added support for advanced apply_top_k_top_p without top_k constraint. [#6098](https://github.com/vllm-project/vllm-ascend/pull/6098)
- **Multimodal**: Parallelized Q/K/V padding in AscendMMEncoderAttention for better performance. [#6204](https://github.com/vllm-project/vllm-ascend/pull/6204)

### Dependencies

- **CANN**: Upgraded to 8.5.0 [#6112](https://github.com/vllm-project/vllm-ascend/pull/6112)
- **torch-npu**: Upgraded to 2.8.0.post1. Please note that the post version will not be installed by default. Please install it by hand from [pypi mirror](https://mirrors.huaweicloud.com/ascend/repos/pypi/torch-npu/). [#3896](https://github.com/vllm-project/vllm-ascend/pull/3896) [#4433](https://github.com/vllm-project/vllm-ascend/pull/4433)
- **triton-ascend**: Upgraded to 3.2.0 [#6105](https://github.com/vllm-project/vllm-ascend/pull/6105)
- **vLLM**: Upgraded to 0.13.0 and dropped 0.12.0 support. [#5146](https://github.com/vllm-project/vllm-ascend/pull/5146)
- **Transformers**: Upgraded to >= 4.57.3 [#5250](https://github.com/vllm-project/vllm-ascend/pull/5250)

### Deprecation & Breaking Changes

- **CPUOffloadingConnector** is deprecated. We'll remove it in the next release. It'll be replaced by CPUOffload feature from vLLM in the future.
- **EPLB config options** have been moved to `eplb_config` in [additional config](https://docs.vllm.ai/projects/ascend/en/latest/user_guide/configuration/additional_config.html). The old ones will be removed in the next release.
- **ProfileExecuteDuration** [feature](https://docs.vllm.ai/projects/ascend/en/latest/developer_guide/performance_and_debug/profile_execute_duration.html) is deprecated. It's replaced by `ObservabilityConfig` from vLLM.
- **Ascend Scheduler** has been dropped. [#4623](https://github.com/vllm-project/vllm-ascend/pull/4623)
- **Torchair** has been dropped. [#4814](https://github.com/vllm-project/vllm-ascend/pull/4814)
- **VLLM_ASCEND_ENABLE_DENSE_OPTIMIZE** is removed and `VLLM_ASCEND_ENABLE_PREFETCH_MLP` is recommended to replace as they were always enabled together. [#5272](https://github.com/vllm-project/vllm-ascend/pull/5272)
- **VLLM_ENABLE_FUSED_EXPERTS_ALLGATHER_EP** is dropped now. [#5270](https://github.com/vllm-project/vllm-ascend/pull/5270)
- **VLLM_ASCEND_ENABLE_NZ** is disabled for float weight case, since we noticed that the performance is not good in some float cases. Feel free to set it to 2 if you make sure it works for your case. [#4878](https://github.com/vllm-project/vllm-ascend/pull/4878)
- **chunked_prefill_for_mla** in `additional_config` is dropped now. [#5296](https://github.com/vllm-project/vllm-ascend/pull/5296)
- **dump_config** in `additional_config` is renamed to `dump_config_path` and the type is changed from `dict` to `string`. [#5296](https://github.com/vllm-project/vllm-ascend/pull/5296)
- **--task parameter** for embedding models is deprecated. [#5257](https://github.com/vllm-project/vllm-ascend/pull/5257)
- **The value of VLLM_ASCEND_ENABLE_MLAPO** env will be set to True by default in the next release. It'll be enabled in decode node by default. Please note that this feature will cost more memory. If you are memory sensitive, please set it to False.

### Documentation

- Added comprehensive developer guides for ACLGraph, MTP, KV Pool, EPLB, and PD disaggregation features
- Added tutorials for multiple models including DeepSeek-V3.2-Exp, Qwen3-Next, and various multimodal models
- Updated FAQ and configuration documentation

### Others

- **OOM Fix**: OOM error on VL models is fixed now. We're keeping observing it. If you hit OOM problem again, please submit an issue. [#5136](https://github.com/vllm-project/vllm-ascend/pull/5136)
- **Qwen3-Next-MTP Accuracy**: Fixed an accuracy bug of Qwen3-Next-MTP when batched inferring. [#4932](https://github.com/vllm-project/vllm-ascend/pull/4932)
- **ZMQ Bug Fix**: Fixed zmq send/receive failed bug. [#5503](https://github.com/vllm-project/vllm-ascend/pull/5503)
- **Weight Transpose**: Fixed weight transpose in RL scenarios. [#5567](https://github.com/vllm-project/vllm-ascend/pull/5567)
- **Eagle3 SP**: Adapted SP to eagle3. [#5562](https://github.com/vllm-project/vllm-ascend/pull/5562)
- **GLM4.6 MTP**: GLM4.6 now supports MTP with fullgraph. [#5460](https://github.com/vllm-project/vllm-ascend/pull/5460)
- **Flashcomm2 Oshard**: Flashcomm2 now works with oshard generalized feature. [#4723](https://github.com/vllm-project/vllm-ascend/pull/4723)
- **Fine-grained Shared Expert Overlap**: Support fine-grained shared expert overlap. [#5962](https://github.com/vllm-project/vllm-ascend/pull/5962)

### Known Issues

- Qwen3-Next doesn't support long sequence scenario, and we should limit `gpu-memory-utilization` according to the doc to run Qwen3-Next. We'll improve it in the next release.
- The functional break on Qwen3-Next when the input/output is around 3.5k/1.5k is fixed, but it introduces a regression on performance. We'll fix it in the next release. [#5357](https://github.com/vllm-project/vllm-ascend/issues/5357)
- There is a precision issue with curl on ultra-short sequences in DeepSeek-V3.2. We'll fix it in the next release. [#5370](https://github.com/vllm-project/vllm-ascend/issues/5370)
