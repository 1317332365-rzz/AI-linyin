<template>
	<view class="u-input-wrap" :class="{ disabled }" :style="wrapStyle">
		<input
			class="u-input-inner"
			:value="innerValue"
			:type="nativeType"
			:password="password"
			:placeholder="placeholder"
			:disabled="disabled"
			:maxlength="maxlength"
			:focus="focus"
			:cursor-spacing="cursorSpacing"
			:confirm-type="confirmType"
			@input="handleInput"
			@focus="handleFocus"
			@blur="handleBlur"
			@confirm="handleConfirm"
		/>
	</view>
</template>

<script>
	export default {
		name: 'u--input',
		props: {
			value: {
				type: [String, Number],
				default: ''
			},
			modelValue: {
				type: [String, Number],
				default: ''
			},
			type: {
				type: String,
				default: 'text'
			},
			password: {
				type: Boolean,
				default: false
			},
			placeholder: {
				type: String,
				default: ''
			},
			disabled: {
				type: Boolean,
				default: false
			},
			maxlength: {
				type: [Number, String],
				default: 140
			},
			focus: {
				type: Boolean,
				default: false
			},
			cursorSpacing: {
				type: [Number, String],
				default: 24
			},
			confirmType: {
				type: String,
				default: 'done'
			},
			customStyle: {
				type: [String, Object],
				default: ''
			}
		},
		computed: {
			innerValue() {
				if (this.modelValue !== '' && this.modelValue !== undefined && this.modelValue !== null) {
					return String(this.modelValue)
				}
				return String(this.value || '')
			},
			nativeType() {
				return this.password ? 'text' : this.type
			},
			wrapStyle() {
				if (!this.customStyle) {
					return ''
				}
				if (typeof this.customStyle === 'string') {
					return this.customStyle
				}
				return this.customStyle
			}
		},
		methods: {
			handleInput(event) {
				const nextValue = event && event.detail ? event.detail.value : ''
				this.$emit('input', nextValue)
				this.$emit('update:modelValue', nextValue)
				this.$emit('change', nextValue)
			},
			handleFocus(event) {
				this.$emit('focus', event)
			},
			handleBlur(event) {
				this.$emit('blur', event)
			},
			handleConfirm(event) {
				this.$emit('confirm', event)
			}
		}
	}
</script>

<style scoped lang="scss">
	.u-input-wrap {
		width: 100%;
		min-height: 84rpx;
		border-radius: 22rpx;
		border: 1rpx solid rgba(116, 173, 165, 0.18);
		background: rgba(7, 24, 26, 0.92);
		padding: 0 22rpx;
		display: flex;
		align-items: center;
	}

	.u-input-wrap.disabled {
		opacity: 0.65;
	}

	.u-input-inner {
		width: 100%;
		height: 84rpx;
		color: #ecfaf6;
		font-size: 28rpx;
	}
</style>
